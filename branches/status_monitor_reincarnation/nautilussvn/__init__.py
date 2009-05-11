version = "0.12-beta1"
APP_NAME = "NautilusSvn"

def package_name():
    """
    Report the application name in a form appropriate for building
    package files.

    """
    return APP_NAME.lower()


def package_version():
    """
    Report the version number of the application, minus any name
    extensions.

    """
    app_version = version.split('-')[0]
    # TODO: sanity-check app_version: make sure it's just digits and dots
    return app_version


def package_identifier():
    """
    Return a package identifier suitable for use in a package file.

    """
    return "%s-%s" % (package_name(), package_version())
