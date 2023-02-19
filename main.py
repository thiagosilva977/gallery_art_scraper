import os
import traceback

from source.test_heni import HeniTrial

if __name__ == '__main__':
    """
    Main task initialization
    
    Initialize this file
    """
    try:
        os.remove('collected_data.json')
    except FileNotFoundError:
        pass
    scraper_class = HeniTrial()
    scraper_class.start_test()
