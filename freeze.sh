#!/bin/bash

env/bin/pip freeze | grep -v "pkg-resources" > requirements.txt
