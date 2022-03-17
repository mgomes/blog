Date: May 29, 2018
Tags: open source, projects

# BLAKE2b for Ruby

[BLAKE2](https://blake2.net) is a cryptographic hash function faster than MD5, SHA-1, SHA-2, and SHA-3, yet is at least as secure as the latest standard SHA-3. It was a final candidate to become SHA-3, but apparently the committee didn't feel like it differed enough from SHA-2. Either way, it is a really fast, secure cryptographic hashing function that I wanted to use in Ruby.

The reference C implementation comes in two flavors:

* **BLAKE2s** is optimized for 8- to 32-bit platforms and produces digests of any size between 1 and 32 bytes. Franck Verrot has already created a wonderful [BLAKE2s](https://github.com/franckverrot/blake2) implementation.
* **BLAKE2b** (or just BLAKE2) is optimized for 64-bit platforms—including NEON-enabled ARMs—and produces digests of any size between 1 and 64 bytes. This is the one I wanted to use for it's performance.

So after modifying Franck Verrot's implementation a bit, I was able to create the [blake2b](https://github.com/mgomes/blake2b) Ruby gem. Unfortunately I had to leave out the NEON support for ARM chips for now since I don't have a machine to test on. I was pretty happy with the resulting performance:

## Performance

BLAKE2b really shines on larger inputs and so the benchmark runs on various input sizes. All tests were run on an iMac 27" Late 2014, 4GHz Core i7 CPU (4790K) w/ SSE4.1 + SSE4.2, 32GB DDR3 RAM.

### 1KB (1M digests)

```
MD5 result: 2.694545999998809 seconds.
SHA2 result: 4.037195000011707 seconds.
SHA512 result: 3.213850000000093 seconds.
BLAKE2s result: 5.6867979999951785 seconds.
BLAKE2b result: 4.375018999999156 seconds.
```

### 50KB (500k digests)

```
MD5 result: 34.33997299999464 seconds.
SHA2 result: 50.161426999999094 seconds.
SHA512 result: 35.24845699999423 seconds.
BLAKE2s result: 64.8592859999917 seconds.
BLAKE2b result: 30.783814999987953 seconds.
```

### 250KB (500k digests)

```
MD5 result: 67.89016799999808 seconds.
SHA2 result: 103.09026799999992 seconds.
SHA512 result: 72.46762200001103 seconds.
BLAKE2s result: 133.5229810000019 seconds.
BLAKE2b result: 64.30263599999307 seconds.
```

## Future

The reference C implementation includes a multi-threaded version called BLAKE2bp. I plan to add BLAKE2bp to this gem so one is able to use either version at runtime.

Lastly, this gem may not even be required once Ruby [issue #12802](https://bugs.ruby-lang.org/issues/12802) is resolved. BLAKE2 will either be included natively into MRI or available through the OpenSSL library.
