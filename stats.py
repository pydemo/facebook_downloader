import time
import sys
from pprint import pprint as pp 
from include.reel_utils import  get_page_metrics
import include.config.init_config as init_config
init_config.init(**{}) 
apc = init_config.apc



      
apc.page_id= '105420925572228'
def main():
    try:
        print("Starting metric collection. Press CTRL+C to stop.")
        while True:
            metrics = get_page_metrics()
            print(f"Metrics collected at {time.strftime('%Y-%m-%d %H:%M:%S')}:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")
            print("-" * 40)
            apc.update_stats(metrics)
            pp(apc.get_today_stats())
            # Wait for 60 seconds before the next collection
            time.sleep(60*5)
    except KeyboardInterrupt:
        print("\nMetric collection stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()