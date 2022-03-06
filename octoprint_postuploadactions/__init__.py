# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from threading import Timer

class ConnectOnUploadPlugin(octoprint.plugin.StartupPlugin, octoprint.plugin.EventHandlerPlugin, octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin, octoprint.plugin.TemplatePlugin):
    CONNECT_DELAY = 5.0
    def on_after_startup(self):
        helpers = self._plugin_manager.get_helpers("mqtt", "mqtt_publish")
        if helpers:
            if "mqtt_publish" in helpers:
                self.mqtt_publish = helpers["mqtt_publish"]
            try:			
                self.mqtt_publish("octoprint/plugin/connectonupload/pub", "OctoPrint-ConnectOnUpload publishing.")
            except:
                self._plugin_manager.send_plugin_message(self._identifier, dict(noMQTT=True))

    def on_event(self, event, payload):
        if event != "Upload":
            return
        if not payload["print"]:
            return
        self._logger.info(payload)
        self._printer.connect(port="AUTO", baudrate="AUTO", profile="_default")
        Timer(self.CONNECT_DELAY, self._printer.select_file, 
            args=[payload["path"], False],kwargs=dict(printAfterSelect=True)).start()

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/postuploadactions.js"],
            "css": ["css/postuploadactions.css"],
            "less": ["less/postuploadactions.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "postuploadactions": {
                "displayName": "Postuploadactions Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "4cello",
                "repo": "OctoPrint-PostUploadActions",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/4cello/OctoPrint-PostUploadActions/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Connect on Upload"
__plugin_version__ = "0.1.0"
__plugin_description__ = "A quick \"Hello World\" example plugin for OctoPrint"

# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ConnectOnUploadPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
