import multiprocessing
from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime

process_label_id = {0: 'a', 1: 'b', 2: 'c'}


def local_time(vector):
    return ' (Vector state={})'.format(vector)


def calc_recv_timestamp(recv_time_stamp, vector):
    for id in range(len(vector)):
        vector[id] = max(recv_time_stamp[id], vector[id])
    return vector


def event(pid, vector):
    vector[pid] += 1
    print('Event happened in {} !'. \
          format(process_label_id[pid]) + local_time(vector))
    return vector


def send_message(pipe, pid, vector):
    vector[pid] += 1
    pipe.send(('MESSAGE', vector))
    print('Message sent from ' + str(process_label_id[pid]) + local_time(vector))
    return vector


def recv_message(pipe, pid, vector):
    message, timestamp = pipe.recv()
    vector = calc_recv_timestamp(timestamp, vector)
    vector[pid] += 1
    print('Message received at ' + str(process_label_id[pid]) + local_time(vector))
    return vector


def process_one(pipe12, vectors):
    pid = 0
    vector = [0, 0, 0]

    # actions
    vector = send_message(pipe12, pid, vector)
    vector = send_message(pipe12, pid, vector)

    vector = event(pid, vector)

    vector = recv_message(pipe12, pid, vector)

    vector = event(pid, vector)
    vector = event(pid, vector)

    vector = recv_message(pipe12, pid, vector)

    vectors[pid] = vector


def process_two(pipe21, pipe23, vectors):
    pid = 1
    vector = [0, 0, 0]

    # actions
    vector = recv_message(pipe21, pid, vector)
    vector = recv_message(pipe21, pid, vector)

    vector = send_message(pipe21, pid, vector)

    vector = recv_message(pipe23, pid, vector)

    vector = event(pid, vector)

    vector = send_message(pipe21, pid, vector)

    vector = send_message(pipe23, pid, vector)
    vector = send_message(pipe23, pid, vector)

    vectors[pid] = vector


def process_three(pipe32, vectors):
    pid = 2
    vector = [0, 0, 0]

    # actions
    vector = send_message(pipe32, pid, vector)

    vector = recv_message(pipe32, pid, vector)

    vector = event(pid, vector)

    vector = recv_message(pipe32, pid, vector)

    vectors[pid] = vector


def main():
    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    # shared variable for return message
    manager = multiprocessing.Manager()
    vectors = manager.dict()

    process1 = Process(target=process_one,
                       args=(oneandtwo, vectors))
    process2 = Process(target=process_two,
                       args=(twoandone, twoandthree, vectors))
    process3 = Process(target=process_three,
                       args=(threeandtwo, vectors))

    # start processes
    process1.start()
    process2.start()
    process3.start()

    # wait until processes finished
    process1.join()
    process2.join()
    process3.join()

    # print output vectors of processes
    for key, vector in sorted(vectors.items()):
        print("Process {} {}".format(process_label_id[key], vector))


if __name__ == '__main__':
    main()
