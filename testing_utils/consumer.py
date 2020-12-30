#!/usr/bin/env python3

import pika
import subprocess
import sys
import json
import signal

def exitting(*args):
    print('Exitting')
    sys.exit(0)

signal.signal(signal.SIGTERM,exitting)
signal.signal(signal.SIGQUIT,exitting)
signal.signal(signal.SIGINT,exitting)

ip=json.loads(subprocess.check_output(["docker inspect docker_queue_1"],shell=True))[0].get('NetworkSettings',{}).get('Networks',{}).get('docker_default',{}).get('IPAddress')
print(ip)
creds=pika.PlainCredentials('analytics','analytics')
conn=pika.ConnectionParameters(ip,5672,'/',creds,socket_timeout=2)


while True:
    connection = pika.BlockingConnection(conn)
    channel = connection.channel()

    i=1
    for method_frame, properties, body in channel.consume('analytics'):
    # Display the message parts and acknowledge the message
    #print(method_frame, properties, body)
        print('#{} {}\n'.format(i,body.decode('utf8')))
        channel.basic_ack(method_frame.delivery_tag)
        i+=1
    # Escape out of the loop after 10 messages
    #if method_frame.delivery_tag == 10:
    #    break

# Cancel the consumer and return any pending messages
requeued_messages = channel.cancel()
print('Requeued %i messages' % requeued_messages)
connection.close()
