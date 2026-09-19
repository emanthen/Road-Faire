FROM node:22-alpine

# npm@latest keeps the CLI itself current, but npm's own bundled internals
# (tar/ip-address/brace-expansion/undici — used by its registry client and tarball
# extraction) lag behind their own upstream CVE fixes even in the newest npm release;
# verified 2026-09-19 against npm@12.0.2, the latest at the time. All four patched
# versions satisfy the semver ranges npm's own dependents (socks, minimatch, node-gyp)
# already declare, so force-installing them in place is safe — confirmed by running a
# real `npm install` afterward, exercising both the tar-extraction and undici-download
# paths end to end. Drop this block once `npm view npm@latest dependencies` shows a
# release that's bumped these on its own; the tarballs below become redundant, not
# harmful, if npm gets there first.
RUN apk update && apk upgrade --no-cache && npm install -g npm@latest && \
    NPM_DIR="$(npm root -g)/npm/node_modules" && \
    mkdir -p /tmp/npm-cve-patch && \
    npm pack tar@7.5.21 ip-address@10.3.1 brace-expansion@5.0.9 undici@6.28.0 \
      --pack-destination /tmp/npm-cve-patch && \
    for spec in tar-7.5.21:tar ip-address-10.3.1:ip-address \
                brace-expansion-5.0.9:brace-expansion undici-6.28.0:undici; do \
      name="${spec%%:*}"; pkg="${spec##*:}"; \
      rm -rf "$NPM_DIR/$pkg" && mkdir -p "$NPM_DIR/$pkg" && \
      tar -xzf "/tmp/npm-cve-patch/$name.tgz" -C "$NPM_DIR/$pkg" --strip-components=1; \
    done && \
    rm -rf /tmp/npm-cve-patch

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
