def find(path, obj, arr='[]', wildcard='*', sep=',', dash='-', depth=0):
    """
     find the specific key's value.
    :param path: str
    :param obj: dict
    :param sep: str
    :param arr: str
    :param wildcard: str
    :return:
    """
    if len(path) == 0:
        return obj

    if obj is None:
        return obj

    if path[0].endswith(arr[1]):
        if type(obj) is list:
            depth += 1
            new_obj = handle_arr_filter(path[0], obj, arr, wildcard, sep, dash)
            return find(path[1:], new_obj, arr, wildcard, sep, dash, depth)
        else:
            raise Exception("dict found but you assumed it's an array.")
    else:
        if type(obj) is list:
            if depth == 0:
                return None
            elif depth == 1:
                # 当上游是数组, 经过筛选后，返回可能还是一个 list，此时可能接着是一个定位符取值
                merged_r = []
                for ele in obj:
                    # 注意，此处仅需提取单级
                    result = find([path[0]], ele, arr, wildcard, sep, dash, depth)
                    merged_r.append(result)
                return find(path[1:], merged_r, arr, wildcard, sep, dash, depth)
            elif depth >= 1:
                merged_res = []
                for ele in obj:
                    # 多级的数组筛选后，会出现多维数组，因此需要逐层解开嵌套的 list.
                    result = find([path[0]], ele, arr, wildcard, sep, dash, depth-1)
                    merged_res.append(result)
                return find(path[1:], merged_res, arr, wildcard, sep, dash, depth)
        elif type(obj) is dict:
            new_res = obj.get(path[0])
            return find(path[1:], new_res, arr, wildcard, sep, dash, depth)
        else:
            print(path, type(obj), obj)
            raise Exception("type error.")


def handle_arr_filter(path, obj, arr='[]', wildcard="*", sep=',', dash='-'):

    selector = path[1:-1]
    result, is_merged = arr_filter(selector, obj, arr, wildcard, sep, dash)
    return result


def arr_filter(selector, obj, arr='[]', wildcard="*", sep=',', dash='-'):
    """
    # 1. 支持全量 [] / [*]
    # 2. 支持索引 [44]
    # 3. 支持半开截断 [1-] / [-7]
    # 4. 支持中间截断 [3-5]
    # 5. 支持组合： [-5, 7-9, 10, 57-]

    :param selector:
    :param obj:
    :param arr:
    :param wildcard:
    :param sep:
    :param dash:
    :return:  tuple: (结果, 是否人工拼接)
    """
    # 1. 支持全量
    if selector == wildcard or selector == '':
        return obj, False

    # 2. 支持索引
    if selector.isdigit():
        if type(obj) is list:
            return obj[int(selector)], False
        else:
            raise Exception("type of obj does not match, it is not list type.")

    # 3. 支持半开截断
    # 4. 支持开区间
    has_sep = selector.count(sep) != 0
    if not has_sep:
        has_dash = selector.count(dash) != 0
        if has_dash:
            left, right = selector.split(dash)
            # print(type(left), type(right))
            # format
            if not left.isdigit():
                left = -1
            if not right.isdigit():
                right = 9223372036854775807

            # convert
            left, right = int(left), int(right)

            merged_res = []
            for index, value in enumerate(obj):
                if left <= index <= right:
                    merged_res.append(value)
            return merged_res, True
        else:
            raise Exception("format error.")
    else:
        # 5. 支持组合, TODO: 注意合并结果
        merged_res = []
        for i in selector.split(sep):
            res, merged = arr_filter(i, obj, arr, wildcard, sep, dash)
            # 如果是拼接的结果，那么需要将其解开后 再合并
            if merged:
                merged_res.extend(res)
            else:
                merged_res.append(res)
        return merged_res, True


if __name__ == "__main__":
    json = {
    "a": {
        "a1": {
            "a1": [
                {
                    "a11": {
                        "a111": [
                            {
                                "a1111": [
                                    11111,
                                    2,
                                    3
                                ]
                            },
                            {
                                "a1111": [
                                    11112,
                                    2,
                                    3
                                ]
                            },
                            {
                                "a1111": [
                                    11113,
                                    2,
                                    3
                                ]
                            }
                        ]
                    }
                },
                {
                    "a11": {
                        "a111": [
                            {
                                "a1111": [
                                    22222,
                                    2,
                                    3
                                ]
                            },
                            {
                                "a1111": [
                                    222223,
                                    2,
                                    3
                                ]
                            },
                            {
                                "a1111": [
                                    222224,
                                    2,
                                    3
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        "a2": {
            "a22": 1
        }
    },
    "b": [
        {
            "b1": [
                0,
                2,
                3
            ],
            "b2": {
                "c1": 1,
                "c2": 2
            },
            "b3": "value3",
            "b4": 0
        },
        {
            "b1": [
                1,
                2,
                3
            ],
            "b2": "value2",
            "b3": "value3",
            "b4": 1
        },
        {
            "b1": [
                2,
                2,
                3
            ],
            "b2": "value2",
            "b3": "value3",
            "b4": 2
        },
        {
            "b1": [
                3,
                2,
                3
            ],
            "b2": "value2",
            "b3": "value3",
            "b4": 3
        },
        {
            "b1": [
                4,
                2,
                3
            ],
            "b2": "value2",
            "b3": "value3",
            "b4": 4
        }
    ]
    }

    res = find("a.a1.a1.[].a11".split('.'), json)
    print(res)
    print('--------1-------')
    res = find("a.a1.a1.[].a11.a111".split('.'), json)
    print(res)
    print('-------2--------')
    res = find("a.a1.a1.[].a11.a111.[].a1111".split('.'), json)
    print(res)
    print('-------3--------')
    res = find("a.a1.a1.[0].a11.a111.[].a1111".split('.'), json)
    print(res)
    print('-------4--------')
    res = find("a.a1.a1.[].a11.a111.[0].a1111".split('.'), json)
    print(res)
    print('-------5--------')
    res = find("a.a1.a1.[0].a11.a111.[0].a1111".split('.'), json)
    print(res)
    print('--------6-------')
    res = arr_filter("-4,5,7,9-10,12-", [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
    print(res)
    print('--------7-------')


