#!/bin/bash

export PYTHONPATH=$GAE_PATH:$PYTHONPATH
export PYTHONPATH=$GAE_PATH/lib/yaml/lib:$PYTHONPATH
py.test $1 front/tests/*
