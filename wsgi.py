#!/usr/bin/env python3
import os

from app import create_app

application = create_app(os.environ.get('IIS_CONFIG', 'default'))
