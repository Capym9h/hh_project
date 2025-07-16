import os
import config


base = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(base, 'super')):
    os.mkdir(os.path.join(base,'super'))

