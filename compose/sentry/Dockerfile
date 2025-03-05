FROM getsentry/sentry:latest

COPY entrypoint-init.sh /entrypoint-init.sh
RUN chmod +x /entrypoint-init.sh

ENTRYPOINT ["/entrypoint-init.sh"]
CMD []
