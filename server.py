import asyncio
import time


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.connected_clients = list()
        self.last_msg_time = dict()

    async def handle_echo(self, reader, writer):
        self.connected_clients.append(writer)
        addr = self.get_addr(writer)
        print(f'{addr[0]}:{addr[1]} is connected.')
        self.last_msg_time[addr] = time.time()
        task_1 = asyncio.get_event_loop().create_task(
            self.receiver(reader, writer)
        )
        task_2 = asyncio.get_event_loop().create_task(
            self.downtime_checker(writer)
        )
        await task_1
        await task_2

    async def downtime_checker(self, writer):
        while True:
            print('checker')
            addr = self.get_addr(writer)
            time_gap = time.time() - self.last_msg_time[addr]
            if time_gap > 30:
                self.connected_clients.remove(writer)
                self.last_msg_time.pop(addr)
                message = 'Close connection: Idle timeout expired.'
                print(
                    f'{self.get_curr_time()} - {addr[0]}:{addr[1]} | {message}'
                )
                writer.write(message.encode('utf8'))
                break
            await asyncio.sleep(30 - time_gap)

    async def receiver(self, reader, writer):
        addr = self.get_addr(writer)
        while writer in self.connected_clients:
            print('reciver')
            data = await reader.read(1000)
            if not data:
                break
            self.last_msg_time[addr] = time.time()
            message = data.decode('utf-8')
            if message != '':
                to_send = ' '.join(
                    [
                        str(self.get_curr_time()),
                        '-',
                        str(addr[0]),
                        ':',
                        str(addr[1]),
                        '|',
                        message,
                    ]
                )
                print(to_send)
                for client in self.connected_clients:
                    if client != writer:
                        client.write(to_send.encode('utf-8'))
        writer.close()

    async def main(self):
        server = await asyncio.start_server(
            self.handle_echo,
            self.host,
            self.port
        )
        addr = server.sockets[0].getsockname()
        print(f'{self.get_curr_time()} - Serving on {addr[0]}:{addr[1]}.')
        async with server:
            await server.serve_forever()

    @staticmethod
    def get_addr(writer):
        return writer.get_extra_info('peername')

    @staticmethod
    def get_curr_time():
        return time.strftime('%X')


if __name__ == '__main__':
    server = Server('127.0.0.1', 8888)
    asyncio.run(server.main())
