const http = require("node:http");

const RELEASE = "intentional-failure-v2";
const STATUS = 500;

const server = http.createServer((request, response) => {
  if (request.method !== "GET" || request.url !== "/health") {
    response.writeHead(404, { "Content-Type": "text/plain", "Cache-Control": "no-store" });
    response.end("not-found\n");
    return;
  }
  const body = JSON.stringify({ release: RELEASE, healthy: false }) + "\n";
  response.writeHead(STATUS, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store"
  });
  response.end(body);
});

const port = Number(process.env.PORT || 8080);
server.listen(port, "0.0.0.0");
