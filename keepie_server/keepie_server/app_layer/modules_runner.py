import threading
from keepie_server.keepie_server.app_layer.configure_server import run_server
from keepie_server.keepie_server.app_layer.data_processor import DataProcessor

def main():
    run_server()
    threading.Thread(DataProcessor().decorate_runs_processing_in_the_loop , args=(DataProcessor().start_full_processing, 1800, False, -1)).start()

if __name__ == "__main__":
    main()