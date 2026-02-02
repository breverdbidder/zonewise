/**
 * ZoneWise.AI Orchestrator Agent
 * 
 * Coordinates development by delegating tasks to specialized sub-agents.
 * Uses Linear as state machine and Arcade MCP for tool access.
 * 
 * @module OrchestratorAgent
 * @version 2.0.0
 * @author Claude AI Architect
 * @license MIT
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

/**
 * Supported agent types for task delegation
 */
type AgentType = 'orchestrator' | 'coding' | 'linear' | 'github' | 'slack';

/**
 * Task priority levels (1 = highest, 4 = lowest)
 */
type PriorityLevel = 1 | 2 | 3 | 4;

/**
 * Possible states for a Linear issue
 */
type IssueState = 'Backlog' | 'In Session' | 'In Progress' | 'Testing' | 'Done' | 'Blocked';

/**
 * Arcade MCP tool definition
 */
interface ArcadeTool {
  readonly name: string;
  readonly description: string;
  readonly parameters?: Record<string, unknown>;
  readonly requiredScopes?: readonly string[];
}

/**
 * Linear issue label
 */
interface IssueLabel {
  readonly name: string;
  readonly color?: string;
}

/**
 * Linear issue structure with strict typing
 */
interface LinearIssue {
  readonly id: string;
  readonly identifier: string;
  readonly title: string;
  readonly state: { readonly name: IssueState };
  readonly priority: PriorityLevel;
  readonly labels: readonly IssueLabel[];
  readonly description?: string;
  readonly createdAt?: string;
  readonly updatedAt?: string;
}

/**
 * Context passed to sub-agents for task execution
 */
interface AgentContext {
  readonly taskId: string;
  readonly title: string;
  readonly description?: string;
  readonly acceptanceCriteria: readonly string[];
  readonly priority: PriorityLevel;
  readonly labels: readonly string[];
}

/**
 * Result of a task delegation to a sub-agent
 */
interface DelegationResult {
  readonly success: boolean;
  readonly agent: AgentType;
  readonly taskId: string;
  readonly result?: Record<string, unknown>;
  readonly error?: DelegationError;
  readonly durationMs: number;
  readonly retryCount: number;
}

/**
 * Structured error for delegation failures
 */
interface DelegationError {
  readonly code: ErrorCode;
  readonly message: string;
  readonly recoverable: boolean;
  readonly details?: Record<string, unknown>;
}

/**
 * Error codes for classification and handling
 */
type ErrorCode = 
  | 'NETWORK_ERROR'
  | 'RATE_LIMITED'
  | 'AUTH_FAILED'
  | 'TIMEOUT'
  | 'INVALID_INPUT'
  | 'AGENT_FAILED'
  | 'CIRCUIT_OPEN'
  | 'UNKNOWN';

/**
 * Session metrics for monitoring and reporting
 */
interface SessionMetrics {
  readonly sessionId: string;
  readonly startTime: Date;
  tasksCompleted: number;
  tasksFailed: number;
  tasksBlocked: number;
  tokensUsed: number;
  readonly delegations: DelegationResult[];
  errors: readonly SessionError[];
}

/**
 * Session-level error tracking
 */
interface SessionError {
  readonly timestamp: Date;
  readonly code: ErrorCode;
  readonly message: string;
  readonly taskId?: string;
  readonly agent?: AgentType;
}

/**
 * Circuit breaker state for resilience
 */
interface CircuitBreakerState {
  failures: number;
  lastFailure: Date | null;
  isOpen: boolean;
}

/**
 * Audit log entry for security tracking
 */
interface AuditLogEntry {
  readonly timestamp: Date;
  readonly sessionId: string;
  readonly action: string;
  readonly agent?: AgentType;
  readonly taskId?: string;
  readonly success: boolean;
  readonly details?: Record<string, unknown>;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * Immutable configuration object
 */
const CONFIG = {
  models: {
    orchestrator: 'claude-sonnet-4-5-20250929',
    coding: 'claude-sonnet-4-5-20250929',
    linear: 'claude-haiku-4-5-20251001',
    github: 'claude-haiku-4-5-20251001',
    slack: 'claude-haiku-4-5-20251001',
  } as const satisfies Record<AgentType, string>,
  
  limits: {
    maxContextTokens: 150000,
    maxTasksPerSession: 10,
    timeoutMinutes: 120,
    checkpointFrequency: 3,
    maxRetries: 3,
    retryDelayMs: [1000, 5000, 15000] as const,
  } as const,
  
  circuitBreaker: {
    failureThreshold: 3,
    resetTimeMs: 60000,
  } as const,
  
  linear: {
    workspaceSlug: 'zonewise',
    projectName: 'ZoneWise.AI V2',
  } as const,
} as const;

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

/**
 * Validates required environment variables
 * @throws Error if required variables are missing
 */
function validateEnvironment(): void {
  const required = ['ANTHROPIC_API_KEY'];
  const optional = ['ARCADE_API_KEY', 'LINEAR_API_KEY', 'SLACK_BOT_TOKEN'];
  
  const missing = required.filter(key => !process.env[key]);
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
  
  const missingOptional = optional.filter(key => !process.env[key]);
  if (missingOptional.length > 0) {
    console.warn(`Warning: Optional environment variables not set: ${missingOptional.join(', ')}`);
  }
}

/**
 * Sanitizes user input to prevent injection attacks
 * @param input - Raw input string
 * @returns Sanitized string
 */
function sanitizeInput(input: string): string {
  if (typeof input !== 'string') {
    return '';
  }
  
  return input
    .replace(/[<>]/g, '') // Remove potential HTML/XML
    .replace(/\$\{[^}]*\}/g, '') // Remove template literals
    .replace(/`/g, "'") // Replace backticks
    .trim()
    .slice(0, 10000); // Limit length
}

/**
 * Validates a Linear issue object
 * @param issue - Issue to validate
 * @returns True if valid
 */
function isValidLinearIssue(issue: unknown): issue is LinearIssue {
  if (!issue || typeof issue !== 'object') return false;
  
  const obj = issue as Record<string, unknown>;
  
  return (
    typeof obj.id === 'string' &&
    typeof obj.identifier === 'string' &&
    typeof obj.title === 'string' &&
    obj.state !== null &&
    typeof obj.state === 'object' &&
    typeof (obj.state as Record<string, unknown>).name === 'string' &&
    typeof obj.priority === 'number' &&
    obj.priority >= 1 &&
    obj.priority <= 4 &&
    Array.isArray(obj.labels)
  );
}

/**
 * Generates a unique session ID
 * @returns UUID-like session identifier
 */
function generateSessionId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 10);
  return `session_${timestamp}_${random}`;
}

// ============================================================================
// ERROR HANDLING UTILITIES
// ============================================================================

/**
 * Classifies an error into a structured DelegationError
 * @param error - Raw error object
 * @returns Structured error with classification
 */
function classifyError(error: unknown): DelegationError {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch') || message.includes('econnrefused')) {
      return {
        code: 'NETWORK_ERROR',
        message: error.message,
        recoverable: true,
        details: { originalError: error.name },
      };
    }
    
    if (message.includes('rate limit') || message.includes('429') || message.includes('too many requests')) {
      return {
        code: 'RATE_LIMITED',
        message: error.message,
        recoverable: true,
        details: { retryAfter: 60000 },
      };
    }
    
    if (message.includes('auth') || message.includes('401') || message.includes('403') || message.includes('unauthorized')) {
      return {
        code: 'AUTH_FAILED',
        message: error.message,
        recoverable: false,
        details: { requiresReauth: true },
      };
    }
    
    if (message.includes('timeout') || message.includes('timed out') || message.includes('etimedout')) {
      return {
        code: 'TIMEOUT',
        message: error.message,
        recoverable: true,
        details: { timeoutMs: CONFIG.limits.timeoutMinutes * 60000 },
      };
    }
    
    return {
      code: 'UNKNOWN',
      message: error.message,
      recoverable: false,
      details: { stack: error.stack },
    };
  }
  
  return {
    code: 'UNKNOWN',
    message: String(error),
    recoverable: false,
  };
}

/**
 * Delays execution for retry backoff
 * @param ms - Milliseconds to wait
 */
async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// ORCHESTRATOR AGENT CLASS
// ============================================================================

/**
 * Main Orchestrator Agent that coordinates task delegation
 */
export class OrchestratorAgent {
  private readonly client: Anthropic;
  private readonly metrics: SessionMetrics;
  private readonly circuitBreakers: Map<AgentType, CircuitBreakerState>;
  private readonly auditLog: AuditLogEntry[];
  private arcadeTools: readonly ArcadeTool[];
  private readonly systemPrompt: string;

  /**
   * Creates a new OrchestratorAgent instance
   * @throws Error if environment validation fails
   */
  constructor() {
    validateEnvironment();
    
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY is required');
    }
    
    this.client = new Anthropic({ apiKey });
    this.metrics = this.initMetrics();
    this.circuitBreakers = this.initCircuitBreakers();
    this.auditLog = [];
    this.arcadeTools = [];
    this.systemPrompt = this.loadSystemPrompt();
    
    this.logAudit('SESSION_STARTED', true);
  }

  /**
   * Initializes session metrics
   */
  private initMetrics(): SessionMetrics {
    return {
      sessionId: generateSessionId(),
      startTime: new Date(),
      tasksCompleted: 0,
      tasksFailed: 0,
      tasksBlocked: 0,
      tokensUsed: 0,
      delegations: [],
      errors: [],
    };
  }

  /**
   * Initializes circuit breakers for all agent types
   */
  private initCircuitBreakers(): Map<AgentType, CircuitBreakerState> {
    const agents: AgentType[] = ['orchestrator', 'coding', 'linear', 'github', 'slack'];
    const breakers = new Map<AgentType, CircuitBreakerState>();
    
    for (const agent of agents) {
      breakers.set(agent, {
        failures: 0,
        lastFailure: null,
        isOpen: false,
      });
    }
    
    return breakers;
  }

  /**
   * Loads system prompt from file with fallback
   */
  private loadSystemPrompt(): string {
    const promptPath = join(__dirname, 'prompts', 'system.md');
    
    if (existsSync(promptPath)) {
      try {
        return readFileSync(promptPath, 'utf-8');
      } catch (err) {
        console.warn('Failed to load system prompt, using default');
      }
    }
    
    return `You are the Orchestrator Agent for ZoneWise.AI. 
Coordinate development by delegating tasks to specialized sub-agents.
Maintain session state via Linear. Follow the delegation decision tree.`;
  }

  /**
   * Records an audit log entry
   */
  private logAudit(
    action: string,
    success: boolean,
    details?: Record<string, unknown>
  ): void {
    const entry: AuditLogEntry = {
      timestamp: new Date(),
      sessionId: this.metrics.sessionId,
      action,
      success,
      details,
    };
    
    this.auditLog.push(entry);
    
    // Also log to console in structured format
    console.log(JSON.stringify({
      level: success ? 'info' : 'error',
      ...entry,
    }));
  }

  /**
   * Checks if circuit breaker allows request
   */
  private checkCircuitBreaker(agent: AgentType): boolean {
    const breaker = this.circuitBreakers.get(agent);
    if (!breaker) return true;
    
    if (breaker.isOpen) {
      const timeSinceFailure = breaker.lastFailure 
        ? Date.now() - breaker.lastFailure.getTime()
        : Infinity;
      
      if (timeSinceFailure > CONFIG.circuitBreaker.resetTimeMs) {
        // Reset circuit breaker (half-open state)
        breaker.isOpen = false;
        breaker.failures = 0;
        this.logAudit('CIRCUIT_BREAKER_RESET', true, { agent });
        return true;
      }
      
      return false;
    }
    
    return true;
  }

  /**
   * Records a failure for circuit breaker
   */
  private recordFailure(agent: AgentType): void {
    const breaker = this.circuitBreakers.get(agent);
    if (!breaker) return;
    
    breaker.failures++;
    breaker.lastFailure = new Date();
    
    if (breaker.failures >= CONFIG.circuitBreaker.failureThreshold) {
      breaker.isOpen = true;
      this.logAudit('CIRCUIT_BREAKER_OPENED', false, { 
        agent, 
        failures: breaker.failures 
      });
    }
  }

  /**
   * Records a success for circuit breaker
   */
  private recordSuccess(agent: AgentType): void {
    const breaker = this.circuitBreakers.get(agent);
    if (!breaker) return;
    
    breaker.failures = 0;
    breaker.isOpen = false;
  }

  /**
   * Initializes Arcade MCP tools
   */
  async initializeArcade(): Promise<void> {
    this.logAudit('ARCADE_INIT_STARTED', true);
    
    const arcadeKey = process.env.ARCADE_API_KEY;
    if (!arcadeKey) {
      console.warn('ARCADE_API_KEY not set, using mock tools');
      this.arcadeTools = this.getMockTools();
      return;
    }
    
    try {
      // TODO: Replace with actual Arcade SDK initialization
      // const arcade = new ArcadeClient({ apiKey: arcadeKey });
      // this.arcadeTools = await arcade.getTools();
      
      this.arcadeTools = this.getMockTools();
      this.logAudit('ARCADE_INIT_COMPLETED', true, { 
        toolCount: this.arcadeTools.length 
      });
    } catch (err) {
      const error = classifyError(err);
      this.logAudit('ARCADE_INIT_FAILED', false, { error });
      this.arcadeTools = this.getMockTools();
    }
  }

  /**
   * Returns mock tools for development/testing
   */
  private getMockTools(): readonly ArcadeTool[] {
    return Object.freeze([
      { name: 'linear_listIssues', description: 'List Linear issues', requiredScopes: ['linear:read'] },
      { name: 'linear_updateIssue', description: 'Update a Linear issue', requiredScopes: ['linear:write'] },
      { name: 'linear_createComment', description: 'Add comment to issue', requiredScopes: ['linear:write'] },
      { name: 'github_createPullRequest', description: 'Create a PR', requiredScopes: ['repo'] },
      { name: 'github_mergePullRequest', description: 'Merge a PR', requiredScopes: ['repo'] },
      { name: 'slack_postMessage', description: 'Post Slack message', requiredScopes: ['chat:write'] },
    ]);
  }

  /**
   * Reads current state from Linear
   */
  async readLinearState(): Promise<readonly LinearIssue[]> {
    this.logAudit('LINEAR_STATE_READ_STARTED', true);
    
    if (!this.checkCircuitBreaker('linear')) {
      this.logAudit('LINEAR_STATE_READ_BLOCKED', false, { reason: 'circuit_open' });
      return [];
    }
    
    try {
      // TODO: Implement actual Linear API call via Arcade
      // const response = await this.callArcadeTool('linear_listIssues', {
      //   filter: { project: { name: { eq: CONFIG.linear.projectName } } }
      // });
      
      const issues: LinearIssue[] = [];
      
      this.recordSuccess('linear');
      this.logAudit('LINEAR_STATE_READ_COMPLETED', true, { 
        issueCount: issues.length 
      });
      
      return issues;
    } catch (err) {
      const error = classifyError(err);
      this.recordFailure('linear');
      this.logAudit('LINEAR_STATE_READ_FAILED', false, { error });
      throw err;
    }
  }

  /**
   * Prioritizes tasks based on priority and state
   * @param issues - List of issues to prioritize
   * @returns Sorted and filtered list of tasks
   */
  prioritizeTasks(issues: readonly LinearIssue[]): readonly LinearIssue[] {
    const validIssues = issues.filter(isValidLinearIssue);
    
    return validIssues
      .filter(issue => 
        issue.state.name !== 'Done' && 
        issue.state.name !== 'Blocked'
      )
      .sort((a, b) => {
        // Priority: 1 (critical) > 2 (high) > 3 (medium) > 4 (low)
        if (a.priority !== b.priority) {
          return a.priority - b.priority;
        }
        // If same priority, prefer those already in progress
        if (a.state.name === 'In Progress' && b.state.name !== 'In Progress') {
          return -1;
        }
        if (b.state.name === 'In Progress' && a.state.name !== 'In Progress') {
          return 1;
        }
        return 0;
      })
      .slice(0, CONFIG.limits.maxTasksPerSession);
  }

  /**
   * Determines which agent should handle a task
   * @param task - Task to analyze
   * @returns Appropriate agent type
   */
  selectAgent(task: LinearIssue): AgentType {
    const labels = task.labels.map(l => l.name.toLowerCase());
    const title = sanitizeInput(task.title).toLowerCase();
    const desc = sanitizeInput(task.description ?? '').toLowerCase();
    
    // Check for explicit agent labels first
    if (labels.includes('agent:coding')) return 'coding';
    if (labels.includes('agent:linear')) return 'linear';
    if (labels.includes('agent:github')) return 'github';
    if (labels.includes('agent:slack')) return 'slack';
    
    // Infer from task content
    const codingKeywords = ['implement', 'create component', 'fix bug', 'refactor', 'write code', 'add feature'];
    const githubKeywords = ['create pr', 'pull request', 'merge', 'branch', 'commit'];
    const slackKeywords = ['notify', 'update team', 'post to slack', 'announce', 'message'];
    
    if (codingKeywords.some(kw => title.includes(kw) || desc.includes(kw))) {
      return 'coding';
    }
    
    if (githubKeywords.some(kw => title.includes(kw) || desc.includes(kw))) {
      return 'github';
    }
    
    if (slackKeywords.some(kw => title.includes(kw) || desc.includes(kw))) {
      return 'slack';
    }
    
    // Default to coding for implementation tasks
    return 'coding';
  }

  /**
   * Delegates a task to the appropriate sub-agent with retry logic
   * @param task - Task to delegate
   * @param agent - Target agent type
   * @returns Delegation result
   */
  async delegateTask(task: LinearIssue, agent: AgentType): Promise<DelegationResult> {
    const startTime = Date.now();
    let retryCount = 0;
    
    this.logAudit('TASK_DELEGATION_STARTED', true, {
      taskId: task.identifier,
      agent,
    });
    
    // Check circuit breaker
    if (!this.checkCircuitBreaker(agent)) {
      const error: DelegationError = {
        code: 'CIRCUIT_OPEN',
        message: `Circuit breaker open for ${agent} agent`,
        recoverable: false,
      };
      
      return {
        success: false,
        agent,
        taskId: task.identifier,
        error,
        durationMs: Date.now() - startTime,
        retryCount: 0,
      };
    }
    
    // Build context for sub-agent
    const context: AgentContext = {
      taskId: task.identifier,
      title: sanitizeInput(task.title),
      description: task.description ? sanitizeInput(task.description) : undefined,
      acceptanceCriteria: this.extractAcceptanceCriteria(task),
      priority: task.priority,
      labels: task.labels.map(l => l.name),
    };
    
    // Retry loop
    while (retryCount <= CONFIG.limits.maxRetries) {
      try {
        const result = await this.callSubAgent(agent, context);
        
        this.recordSuccess(agent);
        this.logAudit('TASK_DELEGATION_COMPLETED', true, {
          taskId: task.identifier,
          agent,
          retryCount,
        });
        
        return {
          success: true,
          agent,
          taskId: task.identifier,
          result,
          durationMs: Date.now() - startTime,
          retryCount,
        };
      } catch (err) {
        const error = classifyError(err);
        retryCount++;
        
        this.logAudit('TASK_DELEGATION_RETRY', false, {
          taskId: task.identifier,
          agent,
          retryCount,
          error,
        });
        
        if (!error.recoverable || retryCount > CONFIG.limits.maxRetries) {
          this.recordFailure(agent);
          
          return {
            success: false,
            agent,
            taskId: task.identifier,
            error,
            durationMs: Date.now() - startTime,
            retryCount,
          };
        }
        
        // Exponential backoff
        const delayMs = CONFIG.limits.retryDelayMs[retryCount - 1] ?? 15000;
        await delay(delayMs);
      }
    }
    
    // Should not reach here, but TypeScript needs this
    return {
      success: false,
      agent,
      taskId: task.identifier,
      error: { code: 'UNKNOWN', message: 'Exceeded retry limit', recoverable: false },
      durationMs: Date.now() - startTime,
      retryCount,
    };
  }

  /**
   * Calls a sub-agent with specific instructions
   * @param agent - Target agent type
   * @param context - Task context
   * @returns Agent response
   */
  private async callSubAgent(
    agent: AgentType, 
    context: AgentContext
  ): Promise<Record<string, unknown>> {
    const model = CONFIG.models[agent];
    
    // Load agent-specific system prompt
    const agentPromptPath = join(__dirname, '..', agent, 'prompts', 'system.md');
    let agentPrompt: string;
    
    if (existsSync(agentPromptPath)) {
      try {
        agentPrompt = readFileSync(agentPromptPath, 'utf-8');
      } catch {
        agentPrompt = `You are the ${agent} agent for ZoneWise.AI. Complete the assigned task professionally and thoroughly.`;
      }
    } else {
      agentPrompt = `You are the ${agent} agent for ZoneWise.AI. Complete the assigned task professionally and thoroughly.`;
    }
    
    // TODO: Implement actual Claude API call with agent-specific tools
    // This is a placeholder that simulates agent behavior
    const response = await this.client.messages.create({
      model,
      max_tokens: 4096,
      system: agentPrompt,
      messages: [{ 
        role: 'user', 
        content: `Execute task:\n${JSON.stringify(context, null, 2)}` 
      }],
    });
    
    // Track token usage
    this.metrics.tokensUsed += (response.usage?.input_tokens ?? 0) + (response.usage?.output_tokens ?? 0);
    
    return { 
      status: 'completed', 
      agent, 
      response: response.content,
    };
  }

  /**
   * Extracts acceptance criteria from task description
   * @param task - Task to analyze
   * @returns List of acceptance criteria
   */
  private extractAcceptanceCriteria(task: LinearIssue): readonly string[] {
    const desc = task.description ?? '';
    const criteria: string[] = [];
    
    // Parse markdown checklist items
    const checklistRegex = /- \[ \] (.+)/g;
    let match;
    
    while ((match = checklistRegex.exec(desc)) !== null) {
      const criterion = sanitizeInput(match[1]);
      if (criterion) {
        criteria.push(criterion);
      }
    }
    
    return Object.freeze(criteria);
  }

  /**
   * Updates Linear with task result
   * @param taskId - Task identifier
   * @param success - Whether task succeeded
   * @param summary - Result summary
   */
  async updateLinearStatus(
    taskId: string,
    success: boolean,
    summary: string
  ): Promise<void> {
    this.logAudit('LINEAR_UPDATE_STARTED', true, { taskId, success });
    
    if (!this.checkCircuitBreaker('linear')) {
      this.logAudit('LINEAR_UPDATE_BLOCKED', false, { reason: 'circuit_open' });
      return;
    }
    
    try {
      // TODO: Implement via Arcade MCP
      // await this.callArcadeTool('linear_updateIssue', {
      //   id: taskId,
      //   state: success ? 'Done' : 'Blocked',
      // });
      // await this.callArcadeTool('linear_createComment', {
      //   issueId: taskId,
      //   body: sanitizeInput(summary),
      // });
      
      console.log(`[Linear] Updated ${taskId}: ${success ? 'Done' : 'Blocked'}`);
      
      this.recordSuccess('linear');
      this.logAudit('LINEAR_UPDATE_COMPLETED', true, { taskId });
    } catch (err) {
      const error = classifyError(err);
      this.recordFailure('linear');
      this.logAudit('LINEAR_UPDATE_FAILED', false, { taskId, error });
    }
  }

  /**
   * Posts session summary to Slack
   */
  async postSlackSummary(): Promise<void> {
    this.logAudit('SLACK_SUMMARY_STARTED', true);
    
    if (!this.checkCircuitBreaker('slack')) {
      this.logAudit('SLACK_SUMMARY_BLOCKED', false, { reason: 'circuit_open' });
      return;
    }
    
    const duration = Math.round(
      (Date.now() - this.metrics.startTime.getTime()) / 60000
    );
    
    const summary = [
      '📊 *ZoneWise.AI Session Summary*',
      `🆔 Session: \`${this.metrics.sessionId}\``,
      `✅ Completed: ${this.metrics.tasksCompleted}`,
      `❌ Failed: ${this.metrics.tasksFailed}`,
      `⚠️ Blocked: ${this.metrics.tasksBlocked}`,
      `⏱️ Duration: ${duration} min`,
      `🔢 Tokens: ${this.metrics.tokensUsed.toLocaleString()}`,
    ].join('\n');
    
    try {
      // TODO: Implement via Arcade MCP
      // await this.callArcadeTool('slack_postMessage', {
      //   channel: '#zonewise-ai-updates',
      //   text: summary,
      // });
      
      console.log('\n' + summary);
      
      this.recordSuccess('slack');
      this.logAudit('SLACK_SUMMARY_COMPLETED', true);
    } catch (err) {
      const error = classifyError(err);
      this.recordFailure('slack');
      this.logAudit('SLACK_SUMMARY_FAILED', false, { error });
    }
  }

  /**
   * Checks if session should continue
   * @returns True if session can continue
   */
  shouldContinue(): boolean {
    const totalTasks = 
      this.metrics.tasksCompleted + 
      this.metrics.tasksFailed + 
      this.metrics.tasksBlocked;
    
    if (totalTasks >= CONFIG.limits.maxTasksPerSession) {
      this.logAudit('SESSION_LIMIT_REACHED', true, { reason: 'max_tasks' });
      return false;
    }
    
    if (this.metrics.tokensUsed >= CONFIG.limits.maxContextTokens) {
      this.logAudit('SESSION_LIMIT_REACHED', true, { reason: 'token_budget' });
      return false;
    }
    
    const elapsedMinutes = 
      (Date.now() - this.metrics.startTime.getTime()) / 60000;
    if (elapsedMinutes >= CONFIG.limits.timeoutMinutes) {
      this.logAudit('SESSION_LIMIT_REACHED', true, { reason: 'timeout' });
      return false;
    }
    
    return true;
  }

  /**
   * Returns session metrics for monitoring
   */
  getMetrics(): Readonly<SessionMetrics> {
    return Object.freeze({ ...this.metrics });
  }

  /**
   * Returns audit log for security review
   */
  getAuditLog(): readonly AuditLogEntry[] {
    return Object.freeze([...this.auditLog]);
  }

  /**
   * Main orchestration loop
   */
  async run(): Promise<SessionMetrics> {
    console.log('🚀 Starting ZoneWise.AI Orchestrator Session');
    console.log(`📋 Session ID: ${this.metrics.sessionId}`);
    console.log(`⏰ Time: ${new Date().toISOString()}`);
    
    try {
      // Initialize Arcade MCP
      await this.initializeArcade();
      
      // Read current state
      const issues = await this.readLinearState();
      console.log(`📥 Found ${issues.length} issues in Linear`);
      
      // Prioritize tasks
      const prioritizedTasks = this.prioritizeTasks(issues);
      console.log(`📊 Processing ${prioritizedTasks.length} prioritized tasks`);
      
      // Main delegation loop
      for (const task of prioritizedTasks) {
        if (!this.shouldContinue()) break;
        
        const agent = this.selectAgent(task);
        console.log(`\n--- Task: ${task.identifier} ---`);
        console.log(`📝 Title: ${task.title}`);
        console.log(`🤖 Agent: ${agent}`);
        
        const result = await this.delegateTask(task, agent);
        this.metrics.delegations.push(result);
        
        if (result.success) {
          this.metrics.tasksCompleted++;
          await this.updateLinearStatus(
            task.identifier,
            true,
            `✅ Completed by ${agent} agent`
          );
        } else {
          this.metrics.tasksFailed++;
          await this.updateLinearStatus(
            task.identifier,
            false,
            `❌ Failed: ${result.error?.message ?? 'Unknown error'}`
          );
        }
        
        // Checkpoint every N tasks
        const totalTasks = this.metrics.tasksCompleted + this.metrics.tasksFailed;
        if (totalTasks % CONFIG.limits.checkpointFrequency === 0) {
          console.log('💾 Checkpointing progress...');
        }
      }
      
      // Post summary
      await this.postSlackSummary();
      
      this.logAudit('SESSION_COMPLETED', true, {
        tasksCompleted: this.metrics.tasksCompleted,
        tasksFailed: this.metrics.tasksFailed,
        tokensUsed: this.metrics.tokensUsed,
      });
      
    } catch (err) {
      const error = classifyError(err);
      this.logAudit('SESSION_ERROR', false, { error });
      
      (this.metrics.errors as SessionError[]).push({
        timestamp: new Date(),
        code: error.code,
        message: error.message,
      });
      
      throw err;
    }
    
    console.log('\n✅ Orchestrator session complete');
    return this.getMetrics();
  }
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

if (require.main === module) {
  const orchestrator = new OrchestratorAgent();
  orchestrator.run()
    .then(metrics => {
      console.log('\n📊 Final Metrics:', JSON.stringify(metrics, null, 2));
      process.exit(0);
    })
    .catch(err => {
      console.error('❌ Session failed:', err);
      process.exit(1);
    });
}

export default OrchestratorAgent;
