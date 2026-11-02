'use strict';

const fs = require('node:fs/promises');

const MissionType = Object.freeze({
    ORGANIZATIONAL: 'organizational',
    PRODUCT: 'product'
});

const MissionStatus = Object.freeze({
    DRAFT: 'draft',
    ACTIVE: 'active',
    RETIRED: 'retired'
});

class MissionValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'MissionValidationError';
    }
}

class Mission {
    constructor({
        name,
        statement,
        purpose,
        type,
        status = MissionStatus.DRAFT,
        strategicThemes = []
    }) {
        this.name = name;
        this.statement = statement;
        this.purpose = purpose;
        this.type = type;
        this.status = status;
        this.strategicThemes = [...strategicThemes];
    }

    validate() {
        if (!this.name?.trim()) {
            throw new MissionValidationError('Mission name cannot be empty.');
        }

        if (!this.statement?.trim()) {
            throw new MissionValidationError(
                `Mission statement for "${this.name}" cannot be empty.`
            );
        }

        if (!this.purpose?.trim()) {
            throw new MissionValidationError(
                `Mission purpose for "${this.name}" cannot be empty.`
            );
        }

        if (this.statement.length > 300) {
            throw new MissionValidationError(
                `Mission statement for "${this.name}" exceeds 300 characters.`
            );
        }

        const themes = this.strategicThemes.map(theme => theme.toLowerCase());
        if (new Set(themes).size !== themes.length) {
            throw new MissionValidationError(
                `Mission "${this.name}" contains duplicate strategic themes.`
            );
        }
    }
}

class ProductMissionModel {
    constructor({ productName, organizationalMission, productMission, metrics }) {
        this.productName = productName;
        this.organizationalMission = organizationalMission;
        this.productMission = productMission;
        this.metrics = new Map(Object.entries(metrics ?? {}));
    }

    validateAlignment() {
        this.organizationalMission.validate();
        this.productMission.validate();

        if (this.organizationalMission.type !== MissionType.ORGANIZATIONAL) {
            throw new MissionValidationError(
                'The parent mission must be organizational.'
            );
        }

        if (this.productMission.type !== MissionType.PRODUCT) {
            throw new MissionValidationError(
                'The product mission must be product-specific.'
            );
        }

        const organizationThemes = new Set(
            this.organizationalMission.strategicThemes.map(
                theme => theme.toLowerCase()
            )
        );

        const productThemes = new Set(
            this.productMission.strategicThemes.map(
                theme => theme.toLowerCase()
            )
        );

        const sharedThemes = [...productThemes].filter(
            theme => organizationThemes.has(theme)
        );

        if (sharedThemes.length === 0) {
            throw new MissionValidationError(
                `Product "${this.productName}" is not aligned with ` +
                'any organizational strategic theme.'
            );
        }

        return sharedThemes.sort();
    }

    calculatePurposeClarity() {
        const tokenize = value =>
            new Set(
                value
                    .toLowerCase()
                    .split(/\s+/)
                    .map(word => word.replace(/[.,:;()]/g, ''))
                    .filter(word => word.length > 3)
            );

        const statementWords = tokenize(this.productMission.statement);
        const purposeWords = tokenize(this.productMission.purpose);

        if (statementWords.size === 0 || purposeWords.size === 0) {
            return 0;
        }

        let overlap = 0;

        for (const word of statementWords) {
            if (purposeWords.has(word)) {
                overlap++;
            }
        }

        return Number(
            ((overlap / Math.max(statementWords.size, purposeWords.size)) * 100)
                .toFixed(2)
        );
    }

    evaluate() {
        const sharedThemes = this.validateAlignment();

        return {
            product: this.productName,
            organizationalMission: this.organizationalMission.statement,
            productMission: this.productMission.statement,
            sharedStrategicThemes: sharedThemes,
            purposeClarityScore: this.calculatePurposeClarity(),
            metricCount: this.metrics.size,
            status: this.productMission.status
        };
    }
}

class MissionEventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(listener);

        return () => {
            this.listeners.get(eventName)?.delete(listener);
        };
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) ?? new Set();

        for (const listener of listeners) {
            listener(payload);
        }
    }
}

async function saveEvaluation(filePath, evaluation) {
    await fs.writeFile(
        filePath,
        JSON.stringify(evaluation, null, 2),
        'utf8'
    );
}

async function loadEvaluation(filePath) {
    const content = await fs.readFile(filePath, 'utf8');
    return JSON.parse(content);
}

async function main() {
    const events = new MissionEventBus();

    events.on('mission:evaluated', evaluation => {
        console.log(
            `Event: product "${evaluation.product}" was evaluated.`
        );
    });

    const organizationalMission = new Mission({
        name: 'Acme Organizational Mission',
        statement:
            'Improve access to trustworthy digital services by making ' +
            'essential customer interactions simpler and more reliable.',
        purpose:
            'Deliver dependable services that solve important customer problems.',
        type: MissionType.ORGANIZATIONAL,
        status: MissionStatus.ACTIVE,
        strategicThemes: [
            'customer trust',
            'simplicity',
            'reliability'
        ]
    });

    const productMission = new Mission({
        name: 'Payments Product Mission',
        statement:
            'Enable customers to complete everyday payments quickly, ' +
            'clearly, and reliably.',
        purpose:
            'Reduce friction in everyday transactions while preserving ' +
            'customer trust and reliability.',
        type: MissionType.PRODUCT,
        status: MissionStatus.ACTIVE,
        strategicThemes: [
            'customer trust',
            'simplicity',
            'reliability'
        ]
    });

    const model = new ProductMissionModel({
        productName: 'Acme Pay',
        organizationalMission,
        productMission,
        metrics: {
            successfulTransactionRate: 99.2,
            paymentCompletionTimeSeconds: 18.5,
            customerSatisfaction: 91.4
        }
    });

    const evaluation = model.evaluate();

    events.emit('mission:evaluated', evaluation);

    const filePath = 'product-mission-evaluation.json';
    await saveEvaluation(filePath, evaluation);
    const persisted = await loadEvaluation(filePath);

    console.log('\nPRODUCT MISSION EVALUATION');
    console.log('==========================');
    console.log(`Product: ${persisted.product}`);
    console.log(`Organizational mission: ${persisted.organizationalMission}`);
    console.log(`Product mission: ${persisted.productMission}`);
    console.log(
        `Shared themes: ${persisted.sharedStrategicThemes.join(', ')}`
    );
    console.log(`Purpose clarity: ${persisted.purposeClarityScore}%`);
    console.log(`Metrics: ${persisted.metricCount}`);
    console.log(`Status: ${persisted.status}`);

    if (persisted.sharedStrategicThemes.length === 0) {
        throw new Error('Product mission failed strategic alignment.');
    }

    try {
        const invalidMission = new Mission({
            name: 'Invalid Mission',
            statement: '',
            purpose: '',
            type: MissionType.PRODUCT
        });

        invalidMission.validate();
    } catch (error) {
        if (error instanceof MissionValidationError) {
            console.log(`\nValidation failure handled: ${error.message}`);
        } else {
            throw error;
        }
    }
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
