import argparse
import time
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, A
from blockchain import SimpleChain

class ChainResolver(BaseResolver):
    def __init__(self, chain: SimpleChain):
        self.chain = chain

    def resolve(self, request, handler):
        qname = str(request.q.qname)
        qname = qname.rstrip('.')
        idx = self.chain.all_records()
        r = idx.get(qname.lower())
        reply = request.reply()
        if r and r.get('safety', 0.0) >= 0.5:
            # Ensure IP is valid (dnslib expects an IPv4 string)
            try:
                reply.add_answer(RR(qname, rdata=A(r['ip']), ttl=60))
            except Exception:
                # If IP invalid, return no answers (NXDOMAIN-like behavior)
                pass
        # else: leave reply without answers (client will interpret)
        return reply

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5053)
    args = parser.parse_args()
    chain = SimpleChain()
    resolver = ChainResolver(chain)
    udp_server = DNSServer(resolver, port=args.port, address='0.0.0.0')
    udp_server.start_thread()
    print(f"DNS server listening on 0.0.0.0:{args.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping DNS server')
