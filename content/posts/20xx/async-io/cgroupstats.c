#include <linux/cgroupstats.h>

static int seqnum = 0;

int open_netlink() {
    struct sockaddr_nl sa = {
        .nl_family = AF_NETLINK,
        .nl_groups = ...
    };

    return socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
}

int send_cgroupstats_request(const int fd) {
    struct nlmsghdr nh = {
        // TODO
    };
    // Send this netlink message
    struct iovec iov = {
        .iov_base = nh,
        .iov_len = nh->nlmsg_len
    };

    // Send to netlink
    struct sockaddr_nl sa = {
        .nl_family = AF_NETLINK
    };
    // Here's the message.
    struct msghdr msg = {
        .msg_name = &sa,
        .msg_namelen = sizeof(sa),
        .msg_iov = &iov,
        .msg_iovlen = 1,
        .msg_control = NULL,
        .msg_controllen = 0,
        .msg_flags = 0
    };

    // Go.
    return sendmsg(fd, &msg, 0);
}

struct cgroupstats get_cgroupstats_response(const int fd) {

}

int main(int argc, char **argv) {
    int fd = open_netlink();

    // refer to Documentation/accounting/getdelays.c
    return;

    struct nlmsghdr *nh;
    struct iovec iov = { nh, nh->nlmsg_len };
    struct msghdr msg;

    msg = { &sa, sizeof(sa), &iov, 1, NULL, 0, 0 };
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    nh->nlmsg_pid = 0;
    nh->nlmsg_seq = __sync_fetch_and_add(&seqnum, 1);
    nh->nlmsg_flags |= NLM_F_ACK;

    sendmsg(fd, &msg, 0);
}
