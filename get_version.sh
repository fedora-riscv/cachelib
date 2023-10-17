#!/bin/sh

PREFIX='constexpr uint64_t kCachelibVersion = '
SUFFIX=';'

echo $(grep "${PREFIX}" CacheLib-*/cachelib/allocator/CacheVersion.h |
	sed -e "s|${PREFIX}||" | sed -e "s|${SUFFIX}||")
