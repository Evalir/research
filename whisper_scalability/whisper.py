class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
# TODO: Get rid of bytes and KB, always print as as MB and above, then %3.1f
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%6.1f%s" % (num, x)
        num /= 1024.0

def magnitude_fmt(num):
    for x in ['','k','m']:
        if num < 1000:
            return "%2d%s" % (num, x)
        num /= 1000

# Color format based on daily bandwidth usage
# <10mb/d = good, <30mb/d ok, <100mb/d bad, 100mb/d+ fail.
def load_color_prefix(load):
    if load < (1024 * 1000 * 10):
        color_level = bcolors.OKBLUE
    elif load < (1024 * 1000 * 30):
        color_level = bcolors.OKGREEN
    elif load < (1024 * 1000 * 100):
        color_level = bcolors.WARNING
    else:
        color_level = bcolors.FAIL
    return color_level

def load_color_fmt(load, string):
    return load_color_prefix(load) + string + bcolors.ENDC

# We assume an envelope is 1kb
envelope_size = 1024

# 100, 10k, 1m - jumping two orders of magnitude
n_users = 10000

# Due to negotiation, data sync, etc
# Rough assumed overhead, constant factor
envelopes_per_message = 10

# Receiving messages per day
# TODO: Split up by channel, etc
received_messages_per_day = 100

def bandwidth_usage(n_users):
    print(n_users)

# We assume a node is not relaying messages, but only sending
# Goal:
# - make it user-bound, not network-bound
# - reasonable bw and fetch time
# ~1GB per month, ~ 30 mb per day, ~1 mb per hour

def case1():
    # Case 1: only receiving messages meant for you

    def load_users(n_users):
        return envelope_size * envelopes_per_message * \
            received_messages_per_day

    def usage_str(n_users):
        load = load_users(n_users)
        return load_color_fmt(load, "For " + magnitude_fmt(n_users) + " users, receiving bandwidth is " + sizeof_fmt(load_users(n_users)) + "/day")

    print bcolors.HEADER + "\nCase 1. Only receiving messages meant for you" + bcolors.ENDC
    print ""
    print "Assumptions:"
    print "- A1. Envelope size (static): " + str(envelope_size) + "kb"
    print "- A2. Envelopes / message (static): " + str(envelopes_per_message)
    print "- A3. Received messages / day (static): " + str(received_messages_per_day)
    print "- A4. Only receiving messages meant for you"
    print ""
    print usage_str(100)
    print usage_str(100 * 100)
    print usage_str(100 * 100 * 100)
    print ""
    print("------------------------------------------------------------")

def case2():
    # Case 2: receiving all messages

    def load_users(n_users):
        return envelope_size * envelopes_per_message * \
            received_messages_per_day * n_users

    def usage_str(n_users):
        load = load_users(n_users)
        return load_color_fmt(load, "For " + magnitude_fmt(n_users) + " users, receiving bandwidth is " + sizeof_fmt(load_users(n_users)) + "/day")

    print bcolors.HEADER + "\nCase 2. Receiving messages for everyone" + bcolors.ENDC
    print ""
    print "Assumptions:"
    print "- A1. Envelope size (static): " + str(envelope_size) + "kb"
    print "- A2. Envelopes / message (static): " + str(envelopes_per_message)
    print "- A3. Received messages / day (static): " + str(received_messages_per_day)
    print "- A4. Received messages for everyone"
    print ""
    print usage_str(100)
    print usage_str(100 * 100)
    print usage_str(100 * 100 * 100)
    print ""
    print("------------------------------------------------------------")



# Assume half of all messages are in 1:1 and group chat
# XXX: Implicitly assume message/envelope ratio same for 1:1 and public,
# probably not true due to things like key negotiation and data sync
private_message_proportion = 0.5

def case3():
    # Case 3: all private messages go over one discovery topic

    # Public scales per usage, all private messages are received
    # over one discovery topic
    def load_users(n_users):
        load_private = envelope_size * envelopes_per_message * \
            received_messages_per_day * n_users
        load_public = envelope_size * envelopes_per_message * \
            received_messages_per_day
        total_load = load_private * private_message_proportion + \
            load_public * (1 - private_message_proportion)
        return total_load

    def usage_str(n_users):
        load = load_users(n_users)
        return load_color_fmt(load, "For " + magnitude_fmt(n_users) + " users, receiving bandwidth is " + sizeof_fmt(load_users(n_users)) + "/day")

    print bcolors.HEADER + "\nCase 3. All private messages go over one discovery topic" + bcolors.ENDC
    print ""
    print "Assumptions:"
    print "- A1. Envelope size (static): " + str(envelope_size) + "kb"
    print "- A2. Envelopes / message (static): " + str(envelopes_per_message)
    print "- A3. Received messages / day (static): " + str(received_messages_per_day)
    print "- A4. Proportion of private messages (static): " + str(private_message_proportion)
    print "- A5. Public messages only received by relevant recipients (static)"
    print "- A6. All private messages are received by everyone (same topic) (static)"
    print ""
    print usage_str(100)
    print usage_str(100 * 100)
    print usage_str(100 * 100 * 100)
    print ""
    print("------------------------------------------------------------")

def case4():
    # Case 4: all private messages are partitioned into shards

    partitions = 5000

    def load_users(n_users):
        if n_users < partitions:
            # Assume spread out, not colliding
            factor_load = 1
        else:
            # Assume spread out evenly, collides proportional to users
            factor_load = n_users / partitions
        load_private = envelope_size * envelopes_per_message * \
            received_messages_per_day * factor_load
        load_public = envelope_size * envelopes_per_message * \
            received_messages_per_day
        total_load = load_private * private_message_proportion + \
            load_public * (1 - private_message_proportion)
        return total_load

    def usage_str(n_users):
        load = load_users(n_users)
        return load_color_fmt(load, "For " + magnitude_fmt(n_users) + " users, receiving bandwidth is " + sizeof_fmt(load_users(n_users)) + "/day")

    print bcolors.HEADER + "\nCase 4. All private messages are partitioned into shards" + bcolors.ENDC
    print ""
    print "Assumptions:"
    print "- A1. Envelope size (static): " + str(envelope_size) + "kb"
    print "- A2. Envelopes / message (static): " + str(envelopes_per_message)
    print "- A3. Received messages / day (static): " + str(received_messages_per_day)
    print "- A4. Proportion of private messages (static): " + str(private_message_proportion)
    print "- A5. Public messages only received by relevant recipients (static)"
    print "- A6. Private messages are partitioned evenly across partition shards (static), n=" + str(partitions)
    print ""
    print usage_str(100)
    print usage_str(100 * 100)
    print usage_str(100 * 100 * 100)
    print ""
    print("------------------------------------------------------------")

# On Bloom filter, false positive rate:
#
# Bloom logic
# f: in_set?(s, x) => (maybe, no)
# if false_positive high => lots of maybe => direct hits
# test happens at routing node and depends on what filter preference peer has,
# OR what request mailserver receives
#
bloom_size = 512     # size of filter, m
bloom_hash_fns = 3   # number of hash functions, k
bloom_elements = 100 # elements in set, n
# assuming optimal number of hash functions, i.e. k=(m/n)ln 2
# (512/100)*math.log(2) ~ 3.46
# Note that this is very sensitive, so if 200 element you want 1 hash fn, and
# if 50 topics you want 7. Understanding the implications using a suboptimal
# number of hash function is left as an exercise to the reader.
#
# Implied false positive rate (https://hur.st/bloomfilter/?n=100&p=&m=512&k=3)
# p=~0.087, roughly.
bloom_false_positive = 0.1 # false positive rate, p
# Sensitivity to n:
# n=50 => p=1%, n=100 => p=10%, n=200 => 30%
#
# Note that false positivity has two faces, one is in terms of extra bandwidth usage
# The other is in terms of anonymity / plausible deniability for listening on topic
# I.e. N envelopes go to node => 1% false positive rate => 1% of N goes to recipient node
# Even if they only wanted 1 message!
#
# The false positive is a factor of total network traffic

case1()
case2()
case3()
case4()


# Ok, let's get serious. What assumptions do we need to encode?
# Also, what did I observe? I observed 15GB/m = 500mb per day.

# Things to encode:
# - Noisy topic
# - Duplicate messages
# - Bloom filter false positives
# - Bugs / invalid messages
# - Offline case dominant

# Now getting somewhere, still big discrepency though. I.e.
# Case 3. All private messages go over one discovery topic

# Assumptions:
# - A1. Envelope size (static): 1024kb
# - A2. Envelopes / message (static): 10
# - A3. Received messages / day (static): 100
# - A4. Proportion of private messages (static): 0.5
# - A5. All private messages are received by everyone (same topic) (static)
# - A6. Public messages only received by relevant recipients (static)

# For 100 users, receiving bandwidth is  49MB/day
# For 10k users, receiving bandwidth is   5GB/day
# For  1m users, receiving bandwidth is 477GB/day

# 50mb*30 = 1.5GB, I see 15GB so x10. What's missing?
# Heavy user, and duplicate messages (peers), Envelope size?
# Say * 4 (size) * 2 (duplicates) * 2 (usage) then it is within x8-16.
# Also missing bloom filter here

# I am also assuming we are roughly 100 users today, is this accurate?
# How many unique public keys have we seen in common chats the last month?

# TODO: It'd be neat if you could encode assumptions set

# Ok, problem. We know case 4 is inaccurate. Ish.
# Duplicate messages, bloom filter. Need to encode these.
# Also heavy usage etc.

# More factors:
# percentage_offline
# - impacts mailservers
# - and also data sync
# duplication_factor
# bad_envelopes
