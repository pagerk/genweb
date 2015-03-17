#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.split(__file__)[0])



from genweb import build_web_pages


if __name__ == '__main__':
    build_web_pages.main()
