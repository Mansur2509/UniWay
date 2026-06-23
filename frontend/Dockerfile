FROM oven/bun:1.2.15-alpine AS dependencies
WORKDIR /app
COPY package.json ./
RUN bun install

FROM oven/bun:1.2.15-alpine AS development
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["bun", "run", "dev", "--hostname", "0.0.0.0"]

