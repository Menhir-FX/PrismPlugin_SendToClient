# PRISM PLUGIN - SendToClient
<div>
<img src="https://img.shields.io/badge/Prism_Pipeline-2.0.15-mediumseagreen" alt="Prism Pipeline Version">
</div>  
<br>
## DESCRIPTION
  This plugin was developped to work with the Prism Pipeline at MenhirFX.
  
  forked from EFV0804/PrismPlugin_SendToClient
  
  This plugin adds a new option when right clicking a scenefile/media/product in the Prism Project Browser. It allows the user to copy the selected media into a new or existing folder, and rename the files with a custom name.
  
  ![menu_contextuel](https://github.com/user-attachments/assets/2519e5c6-fd81-46f7-9259-d42fc672df01)

  The new option offers 2 actions: 
  - The basic send action, which opens a dialog window. The user can set the media name and the export folder name.
  ![dialog](https://github.com/user-attachments/assets/d10cbd8a-0241-4c78-9d5d-ff0b8ba7a410)


  - And the quick send action, which copies the media with the default setting.

## CONFIG
In the Config class, in env.py you can change the value of some parameters:
- MENU_NAME : The option name in the contextual menu.
- ACTION_NAME : The name of the send action.
- QUICK_ACTION_NAME : The name of the quick send action.
- EXPORT_FOLDER : The export folder name, at the project root.
- get_placeholder_export_name(data) : The method that creates a default name for the media being copied.
- get_default_destination_folder_name():  The method that creates a default name for the destination folder (inside the export folder).


## INSTALL
  To install this plugin copy the folder 'SendToClient' into a Prism plugin location.

