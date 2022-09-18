from src.const.global_map import RESOURCE_MAP, CONFIG_SET

import logging
utils_logger = logging.getLogger('utils_logger')
deviation_logger = logging.getLogger('deviation_logger')



# load docusments (stream) from a collection specified by path
def load_firebase_documents(path):
    try:      
        resp = []
        events =  RESOURCE_MAP['firebase_db_client'].collection(path).stream()
        for event in events:
            doc = event.to_dict()
            resp.append(doc)
        return resp
 
    except Exception as e:
        if CONFIG_SET == 'prod':
            deviation_logger.error('Failed to load firebase docuemnts at %s: error: %s' % (path, e), exc_info=True)
            return []
        else:
            raise RuntimeError('Firebase error') from e
