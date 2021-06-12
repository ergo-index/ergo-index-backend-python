import os
import shutil
import traceback

from decouple import config


class ProjectSettings:
    """
    Handles verifying settings and copying over defaults.
    """

    DEFAULT_SETTINGS_FILE = 'backend/project_settings.env'

    @classmethod
    def setup_and_validate_settings(cls) -> None:
        """
        Parses the config file and throws an exception if any settings are missing.
        """

        # Validate settings if present.
        user_settings_filename = '/resources/project_settings.env'
        project_settings_filenames = ['/.env',
                                      '/backend/.env',
                                      '/backend/ergo_index_fund_api/.env']
        if os.path.exists(user_settings_filename):

            # ...copy user settings into the project.
            for project_settings_filename in project_settings_filenames:
                try:
                    os.remove(project_settings_filename)
                except Exception as e:
                    pass
                shutil.copy(user_settings_filename, project_settings_filename)

            # ...test that required settings are present.
            settings_needed = ['REDIS_IP',
                               'REDIS_PORT',
                               'POSTGRES_IP',
                               'POSTGRES_PORT',
                               'POSTGRES_DB',
                               'POSTGRES_USER',
                               'POSTGRES_PASSWORD',
                               'ADMIN_USER',
                               'ADMIN_EMAIL',
                               'ADMIN_PASSWORD',
                               'SECRET_KEY']
            for setting in settings_needed:
                try:
                    config(setting)
                except Exception as e:
                    traceback.print_exc()
                    print(f'ERROR: Add setting named "{setting}" to project_settings.env file.')
            return

        # Provide user with default settings if none are present.
        default_settings_filename = cls.DEFAULT_SETTINGS_FILE
        shutil.copy(default_settings_filename, user_settings_filename)
        raise ValueError('No settings found. Update default settings on the machine: '
                         '~/ergo_index_fund_backend_data/project_settings.env')
