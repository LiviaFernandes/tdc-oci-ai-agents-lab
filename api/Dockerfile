FROM node:20-alpine

WORKDIR /app

COPY api/package.json ./package.json
COPY api/server.js ./server.js
COPY assets/programacao_tdc_floripa_2026.json ./assets/programacao_tdc_floripa_2026.json

ENV NODE_ENV=production
ENV DATA_PATH=/app/assets/programacao_tdc_floripa_2026.json

EXPOSE 3000

CMD ["node", "server.js"]
