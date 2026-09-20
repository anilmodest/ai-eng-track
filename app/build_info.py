"""What is running. The deploy workflow overwrites this file in the copy it ships, so a deployed
service can always say which commit it is, and a rollback is visible as a change in GIT_SHA.

Locally these stay "dev". Environment variables APP_VERSION and GIT_SHA override both.
"""

APP_VERSION = "0.1.0"
GIT_SHA = "dev"
BUILT_AT = "dev"
