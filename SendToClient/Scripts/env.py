
from datetime import datetime

class Config(object):
    # UI
    MENU_NAME = "Send to client"
    ACTION_NAME = "Send to client"
    QUICK_ACTION_NAME = "Quick Send to client"

    # PATHS
    EXPORT_FOLDER = "08_ToClient"


    def get_placeholder_export_name(data):
        """
        Generate a default export name based on the media or product data.

        Args:
            data (dict): Dictionary containing export file or directory metadata.

        Returns:
            str: A string suitable as a default export name.
        """    
        asset_name = ''
        # for media
        if "identifier" in data.keys():
            return data.get('identifier')

        # for product
        if "product" in data.keys():
            return data.get('product')
        
        # for scene files
        else:
            if data.get('type') == 'shot':
                asset_name = data.get('shot')
            elif data.get('type') == 'asset':
                asset_name = data.get('asset_path')
            
        task = data.get('task')
        
        formatted_toClient_media_name = asset_name + '_' + task

        return formatted_toClient_media_name

    def get_default_destination_folder_name():
        """
        Create a default folder name using the current date.

        Returns:
            str: A string formatted as YYMMDD_ to use as a folder name.
        """

        date = datetime.now()
        date = date.strftime('%y%m%d')
        destination_folder = date + '_'
        return destination_folder