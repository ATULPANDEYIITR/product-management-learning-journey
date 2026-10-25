'use strict';

/*
 * SQL-style product analytics using Node.js built-ins.
 * The query functions below mirror SELECT, WHERE, GROUP BY, JOIN,
 * aggregate functions, HAVING, sorting, and parameter validation.
 */

const products = [
  { productId: 1, name: 'Analytics Pro', category: 'Analytics' },
  { productId: 2, name: 'Team Workspace', category: 'Collaboration' },
  { productId: 3, name: 'Mobile Insights', category: 'Analytics' },
];

const users = [
  { userId: 101, country: 'India', channel: 'Organic' },
  { userId: 102, country: 'USA', channel: 'Paid Search' },
  { userId: 103, country: 'India', channel: 'Referral' },
  { userId: 104, country: 'UK', channel: 'Organic' },
  { userId: 105, country: 'USA', channel: 'Paid Search' },
  { userId: 106, country: 'India', channel: 'Referral' },
];

const events = [
  { eventId: 1, userId: 101, productId: 1, type: 'view', date: '2026-03-01', revenue: 0 },
  { eventId: 2, userId: 101, productId: 1, type: 'activation', date: '2026-03-02', revenue: 0 },
  { eventId: 3, userId: 101, productId: 1, type: 'purchase', date: '2026-03-05', revenue: 99 },
  { eventId: 4, userId: 102, productId: 1, type: 'view', date: '2026-03-02', revenue: 0 },
  { eventId: 5, userId: 102, productId: 1, type: 'purchase', date: '2026-03-07', revenue: 149 },
  { eventId: 6, userId: 103, productId: 2, type: 'view', date: '2026-03-03', revenue: 0 },
  { eventId: 7, userId: 103, productId: 2, type: 'activation', date: '2026-03-04', revenue: 0 },
  { eventId: 8, userId: 104, productId: 2, type: 'view', date: '2026-03-05', revenue: 0 },
  { eventId: 9, userId: 105, productId: 3, type: 'view', date: '2026-03-06', revenue: 0 },
  { eventId: 10, userId: 105, productId: 3, type: 'activation', date: '2026-03-07', revenue: 0 },
  { eventId: 11, userId: 105, productId: 3, type: 'purchase', date: '2026-03-08', revenue: 49 },
  { eventId: 12, userId: 106, productId: 1, type: 'view', date: '2026-03-09', revenue: 0 },
  { eventId: 13, userId: 106, productId: 1, type: 'churn', date: '2026-03-20', revenue: 0 },
  { eventId: 14, userId: 101, productId: 1, type: 'purchase', date: '2026-04-02', revenue: 99 },
];

const ALLOWED_EVENTS = new Set(['view', 'signup', 'activation', 'purchase', 'churn']);

function validateDateRange(start, end) {
  const validDate = (value) =>
    /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    !Number.isNaN(Date.parse(`${value}T00:00:00Z`)) &&
    new Date(`${value}T00:00:00Z`).toISOString().slice(0, 10) === value;

  if (!validDate(start) || !validDate(end)) {
    throw new TypeError('Dates must be valid YYYY-MM-DD values.');
  }
  if (start > end) {
    throw new RangeError('Start date must not be after end date.');
  }
}

function validateData() {
  const userIds = new Set();
  for (const user of users) {
    if (!Number.isInteger(user.userId) || userIds.has(user.userId)) {
      throw new Error(`Invalid or duplicate user ID: ${user.userId}`);
    }
    userIds.add(user.userId);
  }

  const productIds = new Set(products.map((product) => product.productId));
  const eventIds = new Set();

  for (const event of events) {
    if (eventIds.has(event.eventId)) {
      throw new Error(`Duplicate event ID: ${event.eventId}`);
    }
    eventIds.add(event.eventId);

    if (!userIds.has(event.userId) || !productIds.has(event.productId)) {
      throw new Error(`Event ${event.eventId} has an unknown foreign key.`);
    }
    if (!ALLOWED_EVENTS.has(event.type)) {
      throw new Error(`Unsupported event type: ${event.type}`);
    }
    if (!Number.isFinite(event.revenue) || event.revenue < 0) {
      throw new Error(`Invalid revenue in event ${event.eventId}`);
    }
    validateDateRange(event.date, event.date);
  }
}

function groupBy(items, keySelector) {
  const groups = new Map();
  for (const item of items) {
    const key = keySelector(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  return groups;
}

function productRevenue(start, end) {
  validateDateRange(start, end);

  // LEFT JOIN semantics: every product remains in the result.
  const purchaseGroups = groupBy(
    events.filter(
      (event) =>
        event.type === 'purchase' &&
        event.date >= start &&
        event.date <= end,
    ),
    (event) => event.productId,
  );

  return products
    .map((product) => {
      const purchases = purchaseGroups.get(product.productId) ?? [];
      const total = purchases.reduce((sum, event) => sum + event.revenue, 0);
      return {
        product: product.name,
        category: product.category,
        purchaseEvents: purchases.length,
        revenue: total,
        averagePurchase: purchases.length
          ? Number((total / purchases.length).toFixed(2))
          : null,
      };
    })
    .sort((a, b) => b.revenue - a.revenue || a.product.localeCompare(b.product));
}

function acquisitionPerformance() {
  const usersById = new Map(users.map((user) => [user.userId, user]));
  const groups = groupBy(users, (user) => user.channel);

  return [...groups.entries()]
    .map(([channel, channelUsers]) => {
      const channelUserIds = new Set(channelUsers.map((user) => user.userId));
      const purchases = events.filter(
        (event) => event.type === 'purchase' && channelUserIds.has(event.userId),
      );
      const payers = new Set(purchases.map((event) => event.userId));
      const revenue = purchases.reduce((sum, event) => sum + event.revenue, 0);

      return {
        channel,
        registeredUsers: channelUsers.length,
        payingUsers: payers.size,
        revenue,
        conversionPercent: Number(
          ((payers.size / channelUsers.length) * 100).toFixed(2),
        ),
      };
    })
    .sort((a, b) => b.revenue - a.revenue);
}

function activationFunnel(start, end) {
  validateDateRange(start, end);
  const filtered = events.filter(
    (event) => event.date >= start && event.date <= end,
  );

  const viewers = new Set(
    filtered.filter((event) => event.type === 'view').map((event) => event.userId),
  );
  const activated = new Set(
    filtered.filter((event) => event.type === 'activation').map((event) => event.userId),
  );
  const payers = new Set(
    filtered.filter((event) => event.type === 'purchase').map((event) => event.userId),
  );

  return {
    viewers: viewers.size,
    activatedUsers: activated.size,
    payingUsers: payers.size,
    activationPerViewerPercent: viewers.size
      ? Number(((activated.size / viewers.size) * 100).toFixed(2))
      : null,
    // These are distinct-user counts, not proof of ordered funnel progression.
  };
}

function dailyRevenue(start, end) {
  validateDateRange(start, end);
  const grouped = groupBy(
    events.filter(
      (event) =>
        event.type === 'purchase' &&
        event.date >= start &&
        event.date <= end,
    ),
    (event) => event.date,
  );

  return [...grouped.entries()]
    .map(([date, rows]) => ({
      date,
      revenue: rows.reduce((sum, event) => sum + event.revenue, 0),
    }))
    .filter((row) => row.revenue > 0)
    .sort((a, b) => a.date.localeCompare(b.date));
}

function printTable(title, rows) {
  console.log(`\n${title}`);
  if (rows.length === 0) {
    console.log('(no rows)');
    return;
  }
  console.table(rows);
}

async function main() {
  validateData();

  // Promise-based execution provides a natural extension point for asynchronous
  // data sources without requiring third-party packages for this local example.
  const reports = await Promise.all([
    Promise.resolve(productRevenue('2026-03-01', '2026-03-31')),
    Promise.resolve(acquisitionPerformance()),
    Promise.resolve([activationFunnel('2026-03-01', '2026-03-31')]),
    Promise.resolve(dailyRevenue('2026-03-01', '2026-03-31')),
  ]);

  printTable('Revenue by product', reports[0]);
  printTable('Acquisition performance', reports[1]);
  printTable('Distinct-user activation funnel', reports[2]);
  printTable('Daily revenue', reports[3]);

  const marchRevenue = reports[0].reduce((sum, row) => sum + row.revenue, 0);
  if (marchRevenue !== 297) {
    throw new Error(`Revenue validation failed: expected 297, received ${marchRevenue}`);
  }

  try {
    validateDateRange('2026-04-01', '2026-03-01');
    throw new Error('Invalid range was accepted.');
  } catch (error) {
    if (!(error instanceof RangeError)) throw error;
    console.log('\nInvalid date range correctly rejected.');
  }
}

main().catch((error) => {
  console.error(`Analytics failed: ${error.message}`);
  process.exitCode = 1;
});
