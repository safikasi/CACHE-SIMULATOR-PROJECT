def is_binary(addr):
    for i in addr:
        if i not in ('0', '1'):
            return False
    return True

def to_decimal(a):
    a = a[::-1]
    dec = 0
    for i in range(len(a)):
        if a[i] == '1':
            dec += 2 ** i
    return dec

def log2(a):
    a = a >> 1
    log = 0
    while a > 0:
        a = a >> 1
        log += 1
    return log

def is_power_2(a):
    return a != 0 and (a & (a - 1)) == 0

def set_cache():
    cache = []
    for _ in range(cache_lines):
        cache.append(['empty'] * (block_size + 2))
    return cache


class Cache:
    def __init__(self, space, lines, block_size, n):
        self.space = space
        self.lines = lines
        self.block_size = block_size
        self.n_way = n

    def display(self):
        for row in self.space:
            for j in range(len(row)):
                if j != 1:
                    end = '' if j == len(row) - 1 else ' , '
                    print(row[j], end=end)
            print()
        print()

    def write_preprocess(self, address):
        block_offset_bits = log2(self.block_size)
        block_offset_binary = address[address_bit_count - block_offset_bits:]
        block_offset_decimal = to_decimal(block_offset_binary)

        block_number_binary = address[:address_bit_count - block_offset_bits]
        block_number_decimal = to_decimal(block_number_binary)

        if choice[mapping_choice] == 'fully':
            return 0, self.lines, block_number_binary, block_offset_decimal, ''
        else:
            total_sets = int(self.lines / self.n_way)
            target_set = block_number_decimal % total_sets
            start_line = self.n_way * target_set
            end_line = start_line + self.n_way
            line_bits = log2(total_sets)
            tag = address[:address_bit_count - block_offset_bits - line_bits]
            return start_line, end_line, tag, block_offset_decimal, target_set

    def read_cache(self, address):
        global counter
        if not is_binary(address) or len(address) != address_bit_count:
            print("invalid address")
            return False

        start_line, end_line, tag, block_offset_decimal, set_number = self.write_preprocess(address)

        for i in range(start_line, end_line):
            if self.space[i][0] == tag:
                print("cache hit")
                self.space[i][1] = counter
                counter += 1
                print(self.space[i][2:])
                if self.space[i][block_offset_decimal + 2] == 'filled':
                    print("value of word - not specified")
                else:
                    print(f"value of word - {self.space[i][block_offset_decimal + 2]}")
                return True

        print("cache miss")
        return False

    def write_cache(self, address, value):
        global counter
        value = value.split(" ")
        if len(value) != self.block_size:
            print("invalid data size")
            return False
        for v in value:
            if not v.isnumeric():
                print("invalid data values")
                return False

        if not is_binary(address) or len(address) != address_bit_count:
            print("invalid address")
            return False

        start_line, end_line, tag, block_offset_decimal, set_number = self.write_preprocess(address)

        for i in range(start_line, end_line):
            if self.space[i][0] == tag:
                print("block already present")
                return True

        filled = False
        for i in range(start_line, end_line):
            if self.space[i][0] == 'empty':
                self.space[i][0] = tag
                self.space[i][1] = counter
                counter += 1
                for j in range(2, block_size + 2):
                    self.space[i][j] = value[j - 2]
                filled = True
                break

        if not filled:
            print('overwriting existing block')
            replace_index = start_line
            min_counter = self.space[replace_index][1]
            for i in range(start_line + 1, end_line):
                if self.space[i][1] < min_counter:
                    min_counter = self.space[i][1]
                    replace_index = i

            if set_number == '':
                print(f"replaced block number = {to_decimal(self.space[replace_index][0])}")
            else:
                replaced_block = (to_decimal(self.space[replace_index][0]) << log2(int(self.lines / self.n_way))) + \
                                 to_decimal(address[len(tag):address_bit_count - log2(self.block_size)])
                print(f"replaced block number = {replaced_block}")

            self.space[replace_index][0] = tag
            self.space[replace_index][1] = counter
            counter += 1
            for j in range(2, block_size + 2):
                self.space[replace_index][j] = value[j - 2]

        return True


# ----------------------------
# Main Program
# ----------------------------
cache_size = cache_lines = block_size = n = -1
address_bit_count = 16
counter = 0

while not (is_power_2(cache_size) and is_power_2(cache_lines) and is_power_2(block_size) and cache_size == cache_lines * block_size):
    cache_size = int(input("Enter cache size: "))
    cache_lines = int(input("Enter cache lines: "))
    block_size = int(input("Enter block size: "))

mapping_choice = -1
choice = {1: "direct", 2: "fully", 3: "n-way"}
while mapping_choice not in choice:
    mapping_choice = int(input("Press 1 for direct mapping\nPress 2 for Associative mapping\nPress 3 for n-way set associative\n"))

if choice[mapping_choice] == 'n-way':
    while not is_power_2(n):
        n = int(input("Enter value of n in n-way mapping (blocks per set): "))
elif choice[mapping_choice] == 'direct':
    n = 1
else:
    n = cache_lines

print(choice[mapping_choice])
print(n)

empty_cache = set_cache()
cache1 = Cache(empty_cache, cache_lines, block_size, n)
cache1.display()

operation = ''
while operation.lower() != 'q':
    operation = input("Press 1 to read\nPress 2 to write\nPress q to quit\n")
    if operation == '1':
        cache_address = input("Enter address in binary: ")
        if cache1.read_cache(cache_address):
            print("success!")
        else:
            print("fail!")
    elif operation == '2':
        physical_address = input("Enter the address in binary: ")
        value = input("Enter the value of words in binary (space-separated): ")
        if cache1.write_cache(physical_address, value):
            print("success!")
        else:
            print("fail!")
    cache1.display()
