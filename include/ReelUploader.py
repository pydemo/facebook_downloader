import os, sys, time
import traceback
from pprint import pformat
from os.path import isfile, join
from pprint import pprint as pp

from include.video_utils import validate_reel_for_facebook

from include.reel_utils import init_upload, check_status,publish, get_page_metrics,   wait_for_reel_publishing, process_upload
from pubsub import pub

import include.config.init_config as init_config 
apc = init_config.apc


global_self=None

def log(*args):
    msg=' '.join([str(arg) for arg in args])
    current_instance = ReelUploader.get_current_instance()  # Get the current instance of ReelUploader
    print(msg)
    pub.sendMessage('on_log', msg=msg, scope_id=current_instance.scope_id, task_id=current_instance.task_id, file_id=current_instance.file_id)


class ReelUploader  ():
    _current_instance = None  # Class-level variable to hold the current instance

    def __init__(self, scope_id, task):
        ReelUploader._current_instance = self
        self.scope_id = scope_id
        self.task=task
        self.user_id= task.user_id
        self.task_id= task.task_id
        self.page_id= task.page_id
        self.file_id = task.file_id
        self.file_path=task.file_path
        self.reel_descr=task.reel_descr
        self.page_name=task.page_name
    @classmethod
    def get_current_instance(cls):
        # Return the current instance or raise an exception if not set
        if cls._current_instance is None:
            raise Exception("No current instance set")
        return cls._current_instance
            
    def test(self):
        log('test 1')
        self.log('test 2')
    

    def log(self, msg): 
        log(msg)
    def send(self, msg, tag='reel_file_name_changed'):
        pub.sendMessage(tag, value=msg, scope_id=self.scope_id, task_id=self.task_id, file_id=self.file_id)
    def status(self, status):
        self.send(status,'set_reel_status')
    def upload(self):
        print("Uploading reel to the cloud")
        if 1:

            self.on_validate()
            self.on_upload()
            wait_for_reel_publishing(1, 10)
            self.on_publish()
            self.on_status()        
    def wait_on_reel(self)  :
        self.status('WAIT_ON_REEL')
        wait_for_reel_publishing(self.user_id, self.page_id, self.reel_id, 1, 10)
        self.status('WAIT_DONE')
    def on_validate(self):
        
        file_path = self.file_path
        log(f'Validating file: {file_path}\n')

        new_file_path= validate_reel_for_facebook(file_path)
        if new_file_path!=file_path:
            log(f'File validated: {file_path}\n')
            self.send(new_file_path)
            self.file_path=new_file_path
        


    def on_publish(self, event=None):
        self.status('PUBLISHING')
        status=check_status(self.user_id, self.page_id, self.reel_id)
        log(self.pp(status))
        status=status['status']
        video_status= status['video_status']    
        log('video_status:',video_status)
        copyright=status['copyright_check_status']['status']
        log('copyright:',copyright)
        log('Publishing...')
        publish(self.user_id, self.page_id, self.reel_id, self.reel_descr)
        self.status('PUBLISHED')
        time.sleep(5)
        status=check_status(self.user_id, self.page_id, self.reel_id)
        log(self.pp(status))

        
        

    def on_upload(self, event=None):
        self.status('UP_STARTED')
        file_path = self.file_path
        pp(file_path)
        if not  isfile(file_path):
            
            raise   Exception(f"File not found: {file_path}")
        if 1:
            directory, basename = os.path.split(file_path)

            print("Directory:", directory)
            print("Base Name:", basename)
            if 0:
                new_fn= join(directory, f'_{basename}')
                if not isfile(new_fn):
                    os.rename(file_path, new_fn)
            new_fn= file_path
            assert isfile(new_fn),new_fn
            if 1:
                log(f'File renamed: {new_fn}\n')
                self.send(new_fn)
                self.file_path=new_fn
            
        if not os.path.exists(new_fn):
            
            raise ValueError(f"File not found: {new_fn}")
        log(f"Uploading file: {new_fn}\n")
        
        if 1:
            log('Uploading...')
            try:
                log('Validating reel length...')
                assert self.page_id,self.page_id
                assert apc.pages[self.page_id].page_name==self.page_name,(apc.pages[self.page_id].page_name,self.page_name)
                try:
                    self.reel_id=reel_id= init_upload(user_id=self.user_id, page_id=self.page_id) 
                    #self.reel_hl.SetURL(f'https://www.facebook.com/reel/{apc.reel_id}')
                except Exception as e:
                    log(f"Error during upload: {str(e)}\n")
                    #sys.stdout = old_stdout
                    raise e 
                log(f'Allocated reel_id:  {reel_id}')
                self.send(reel_id,'allocated_reel_id')

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                detailed_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                log(detailed_traceback)
                #sys.stdout = old_stdout
                raise e
            
            if isfile(new_fn):
                file_size = os.path.getsize(new_fn)
                file_data= open(new_fn, 'rb')
                print(file_size)
       
                process_upload( file_size, file_data, self.page_id, self.reel_id)




                
            else:
                
                log('Cannot process upload: File not found', new_fn)
        
        assert self.reel_id
        log(f'https://www.facebook.com/reel/{self.reel_id}')   
        #log('Done')
        
        #sys.stdout = old_stdout

        log("Upload completed successfully.\n")
        self.status('UPLOADED')
        
    def on_status(self, event=None):
        
        get_page_metrics()
        try:
            status=check_status()
            log(self.pp(status))
            
        except Exception as e:

            log(f"Error during status check: {str(e)}\n")
            raise e
        finally:
            self.status_btn.Enable()
        print(f'https://www.facebook.com/reel/{apc.reel_id}')   
        print('on_status Done')

    def pp(slef, dd):
        return pformat(dd, indent=2, width=80) +os.linesep        
    

 