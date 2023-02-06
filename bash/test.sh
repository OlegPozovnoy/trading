#!/bin/bash
echo cd "$(dirname "$0")"
echo $(builtin cd $(dirname $0); pwd)