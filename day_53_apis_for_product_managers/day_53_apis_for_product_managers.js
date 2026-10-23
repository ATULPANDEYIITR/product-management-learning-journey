'use strict';

/*
 * Product Manager API Explorer
 *
 * This Node.js program models an HTTP API as an event-driven service.
 * It emphasizes:
 * - resources and REST endpoints
 * - HTTP methods and status codes
 * - bearer authentication
 * - asynchronous request handling
 * - validation
 * - ETag-based optimistic concurrency
 * - rate limiting
 * - API documentation
 *
 * No external npm packages are required.
 */

const http = require('node:http');
const crypto = require('node:crypto');

const PORT = Number(process.env.PORT || 8080);

const API_KEYS = new Map([
  ['pm-demo-key', 'product-manager'],
  ['admin-demo-key', 'administrator']
]);

const products = new Map([
  [1, {
    id: 1,
    name: 'Analytics Pro',
    category: 'analytics',
    price: 49.99,
    active: true,
    version: 1,
    updatedAt: new Date().toISOString()
  }],
  [2, {
    id: 2,
    name: 'Team Workspace',
    category: 'collaboration',
    price: 19.99,
    active: true,
    version: 1,
    updatedAt: new Date().toISOString()
  }]
]);

let nextProductId = 3;

const rateLimits = new Map();
const RATE_LIMIT_MAX = 20;
const RATE_LIMIT_WINDOW_MS = 60_000;

const endpointDocumentation = [
  {
    method: 'GET',
    path: '/api/v1/products',
    description: 'List products with optional category, active, limit and offset filters.'
  },
  {
    method: 'GET',
    path: '/api/v1/products/{id}',
    description: 'Retrieve a single product and its current ETag.'
  },
  {
    method: 'POST',
    path: '/api/v1/products',
    description: 'Create a product.'
  },
  {
    method: 'PATCH',
    path: '/api/v1/products/{id}',
    description: 'Partially update a product using If-Match.'
  },
  {
    method: 'DELETE',
    path: '/api/v1/products/{id}',
    description: 'Delete a product; administrator access is required.'
  }
];

class APIError extends Error {
  constructor(status, message, details = undefined) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

function sendJSON(response, status, body, headers = {}) {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    ...headers
  });

  if (status === 204) {
    response.end();
    return;
  }

  response.end(JSON.stringify(body));
}

function sendError(response, error) {
  const status = error instanceof APIError ? error.status : 500;

  const body = {
    error: error instanceof APIError
      ? error.message
      : 'Internal server error'
  };

  if (error instanceof APIError && error.details) {
    body.details = error.details;
  }

  // Internal exceptions are intentionally not exposed to API clients.
  if (!(error instanceof APIError)) {
    console.error(error);
  }

  sendJSON(response, status, body);
}

function authenticate(request) {
  const authorization = request.headers.authorization || '';

  if (!authorization.startsWith('Bearer ')) {
    throw new APIError(401, 'Bearer authentication is required');
  }

  const token = authorization.slice('Bearer '.length).trim();
  const role = API_KEYS.get(token);

  if (!role) {
    throw new APIError(401, 'Invalid API token');
  }

  return { token, role };
}

function enforceRateLimit(token) {
  const now = Date.now();

  const timestamps = (rateLimits.get(token) || [])
    .filter(timestamp => now - timestamp < RATE_LIMIT_WINDOW_MS);

  if (timestamps.length >= RATE_LIMIT_MAX) {
    throw new APIError(429, 'Rate limit exceeded');
  }

  timestamps.push(now);
  rateLimits.set(token, timestamps);
}

function createETag(product) {
  const material = `${product.id}:${product.version}:${product.updatedAt}`;

  return `"${crypto
    .createHash('sha256')
    .update(material)
    .digest('hex')
    .slice(0, 16)}"`;
}

function validateProductPayload(body, partial = false) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    throw new APIError(400, 'Request body must be a JSON object');
  }

  const allowed = new Set(['name', 'category', 'price', 'active']);

  for (const key of Object.keys(body)) {
    if (!allowed.has(key)) {
      throw new APIError(400, `Unknown field: ${key}`);
    }
  }

  if (!partial) {
    for (const required of ['name', 'category', 'price']) {
      if (!(required in body)) {
        throw new APIError(400, `Missing required field: ${required}`);
      }
    }
  }

  if ('name' in body &&
      (typeof body.name !== 'string' || !body.name.trim())) {
    throw new APIError(400, 'name must be a non-empty string');
  }

  if ('category' in body &&
      (typeof body.category !== 'string' || !body.category.trim())) {
    throw new APIError(400, 'category must be a non-empty string');
  }

  if ('price' in body &&
      (typeof body.price !== 'number' ||
       !Number.isFinite(body.price) ||
       body.price < 0)) {
    throw new APIError(400, 'price must be a non-negative number');
  }

  if ('active' in body && typeof body.active !== 'boolean') {
    throw new APIError(400, 'active must be boolean');
  }
}

async function readJSON(request) {
  return new Promise((resolve, reject) => {
    let raw = '';
    let size = 0;
    const MAX_BODY_SIZE = 1_000_000;

    request.on('data', chunk => {
      size += Buffer.byteLength(chunk);

      if (size > MAX_BODY_SIZE) {
        reject(new APIError(413, 'Request body is too large'));
        request.destroy();
        return;
      }

      raw += chunk;
    });

    request.on('end', () => {
      if (!raw.trim()) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new APIError(400, 'Request body contains invalid JSON'));
      }
    });

    request.on('error', reject);
  });
}

function parseProductId(pathname) {
  const match = pathname.match(/^\/api\/v1\/products\/(\d+)$/);

  if (!match) {
    throw new APIError(404, 'Product endpoint not found');
  }

  const id = Number(match[1]);

  if (!Number.isSafeInteger(id)) {
    throw new APIError(400, 'Invalid product ID');
  }

  return id;
}

function listProducts(url) {
  let result = [...products.values()];

  const category = url.searchParams.get('category');
  const active = url.searchParams.get('active');
  const limit = Number(url.searchParams.get('limit') || 10);
  const offset = Number(url.searchParams.get('offset') || 0);

  if (!Number.isInteger(limit) || limit < 1 || limit > 50) {
    throw new APIError(400, 'limit must be an integer from 1 to 50');
  }

  if (!Number.isInteger(offset) || offset < 0) {
    throw new APIError(400, 'offset must be a non-negative integer');
  }

  if (category) {
    result = result.filter(
      product => product.category.toLowerCase() === category.toLowerCase()
    );
  }

  if (active !== null) {
    if (!['true', 'false'].includes(active)) {
      throw new APIError(400, 'active must be true or false');
    }

    const expected = active === 'true';
    result = result.filter(product => product.active === expected);
  }

  const total = result.length;

  return {
    items: result.slice(offset, offset + limit),
    total,
    limit,
    offset
  };
}

async function route(request, response) {
  const url = new URL(request.url, `http://${request.headers.host}`);

  if (!url.pathname.startsWith('/api/')) {
    throw new APIError(404, 'API endpoint not found');
  }

  const { token, role } = authenticate(request);
  enforceRateLimit(token);

  if (request.method === 'GET' && url.pathname === '/api/v1/products') {
    return sendJSON(response, 200, listProducts(url));
  }

  if (request.method === 'POST' && url.pathname === '/api/v1/products') {
    if (!['product-manager', 'administrator'].includes(role)) {
      throw new APIError(403, 'Product creation is not permitted');
    }

    const body = await readJSON(request);
    validateProductPayload(body);

    const product = {
      id: nextProductId++,
      name: body.name.trim(),
      category: body.category.trim().toLowerCase(),
      price: body.price,
      active: body.active ?? true,
      version: 1,
      updatedAt: new Date().toISOString()
    };

    products.set(product.id, product);

    return sendJSON(
      response,
      201,
      product,
      {
        Location: `/api/v1/products/${product.id}`,
        ETag: createETag(product)
      }
    );
  }

  if (url.pathname.startsWith('/api/v1/products/')) {
    const id = parseProductId(url.pathname);
    const product = products.get(id);

    if (!product) {
      throw new APIError(404, 'Product not found');
    }

    if (request.method === 'GET') {
      return sendJSON(
        response,
        200,
        product,
        { ETag: createETag(product) }
      );
    }

    if (request.method === 'PATCH') {
      if (!['product-manager', 'administrator'].includes(role)) {
        throw new APIError(403, 'Product updates are not permitted');
      }

      const expectedETag = request.headers['if-match'];
      const currentETag = createETag(product);

      if (expectedETag !== currentETag) {
        throw new APIError(
          412,
          'If-Match does not identify the current resource version'
        );
      }

      const body = await readJSON(request);
      validateProductPayload(body, true);

      if ('name' in body) product.name = body.name.trim();
      if ('category' in body) product.category = body.category.trim().toLowerCase();
      if ('price' in body) product.price = body.price;
      if ('active' in body) product.active = body.active;

      product.version += 1;
      product.updatedAt = new Date().toISOString();

      return sendJSON(
        response,
        200,
        product,
        { ETag: createETag(product) }
      );
    }

    if (request.method === 'DELETE') {
      if (role !== 'administrator') {
        throw new APIError(403, 'Administrator role required');
      }

      products.delete(id);
      return sendJSON(response, 204, null);
    }
  }

  throw new APIError(405, 'HTTP method is not supported for this endpoint');
}

function startServer() {
  const server = http.createServer(async (request, response) => {
    try {
      await route(request, response);
    } catch (error) {
      sendError(response, error);
    }
  });

  server.listen(PORT, () => {
    console.log(`Product API listening on http://localhost:${PORT}`);
  });

  return server;
}

function printDocumentation() {
  console.log('\nAPI documentation\n');

  for (const endpoint of endpointDocumentation) {
    console.log(
      `${endpoint.method.padEnd(7)} ${endpoint.path.padEnd(32)} ${endpoint.description}`
    );
  }
}

if (require.main === module) {
  printDocumentation();
  startServer();
}
