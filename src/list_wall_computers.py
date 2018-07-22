from __future__ import print_function

from Pyro4 import errors, naming


def print_list_result():
    try:
        name_server = naming.locateNS()
        result_dict = name_server.list(return_metadata=True)
    except errors.PyroError as x:
        print("Error: %s" % x)
        return

    result_list = []
    for name, (uri, metadata) in sorted(result_dict.items()):
        # print("%s --> %s" % (name, uri))
        print(name)
        result_list.append(name)
        if metadata:
            print("    metadata:", metadata)
    return result_list


if __name__ == "__main__":
    print_list_result()
