import json
import time
import hashlib
from typing import List, Dict

CHAIN_FILE = 'chain.json'

class Block:
    def __init__(self, index: int, timestamp: float, records: List[Dict], prev_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.records = records  # list of {domain, ip, added_by, safety, meta}
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'records': self.records,
            'prev_hash': self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class SimpleChain:
    def __init__(self, path=CHAIN_FILE):
        self.path = path
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
                # data is a list of serialised blocks; reconstruct Block objects
                self.chain = []
                for b in data:
                    # expected keys: index, timestamp, records, prev_hash, hash
                    blk = Block(b['index'], b['timestamp'], b['records'], b['prev_hash'])
                    # override computed hash to keep stored hash (for immutability demo)
                    blk.hash = b.get('hash', blk.hash)
                    self.chain.append(blk)
        except Exception:
            self.chain = [self.genesis_block()]
            self._write_chain()

    def genesis_block(self):
        return Block(0, time.time(), [{'note':'genesis'}], '0')

    def add_block(self, records: List[Dict]):
        if not records:
            return None
        last = self.chain[-1]
        block = Block(len(self.chain), time.time(), records, last.hash)
        self.chain.append(block)
        self._write_chain()
        return block

    def _write_chain(self):
        serial = []
        for b in self.chain:
            serial.append({
                'index': b.index,
                'timestamp': b.timestamp,
                'records': b.records,
                'prev_hash': b.prev_hash,
                'hash': b.hash
            })
        with open(self.path, 'w') as f:
            json.dump(serial, f, indent=2)

    def all_records(self):
        # Flatten records into a dict: domain -> last record
        idx = {}
        for b in self.chain:
            for r in b.records:
                d = r.get('domain')
                if d:
                    idx[d.lower()] = r
        return idx

# quick test
if __name__ == '__main__':
    sc = SimpleChain()
    sc.add_block([{'domain':'example.com','ip':'93.184.216.34','added_by':'local','safety':0.9}])
    print(sc.all_records())
