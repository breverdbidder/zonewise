/**
 * ZoneWise.AI Orchestrator Agent
 * 
 * Coordinates development by delegating tasks to specialized sub-agents.
 * Uses Linear as state machine and Arcade MCP for tool access.
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { join } from 'path';

// Types
interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  state: { name: string };
  priority: number;
  labels: { name: string }[];
  description?: string;
}

interface DelegationResult {
  success: boolean;
  agent: string;
  taskId: string;
  result?: any;
  error?: string;
  durationMs: number;
}

interface SessionMetrics {
  startTime: Date;
  tasksCompleted: number;
  tasksFailed: number;
  tasksBlocked: number;
  tokensUsed: number;
  delegations: DelegationResult[];
}

// Configuration
const CONFIG = {
  models: {
    orchestrator: 'claude-sonnet-4-5-20250929',
    coding: 'claude-sonnet-4-5-20250929',
    linear: 'claude-haiku-4-5-20251001',
    github: 'claude-haiku-4-5-20251001',
    slack: 'claude-haiku-4-5-20251001',
  },
  limits: {
    maxContextTokens: 150000,
    maxTasksPerSession: 10,
    timeoutMinutes: 120,
    checkpointFrequency: 3,
    maxRetries: 3,
  },
  linear: {
    workspaceSlug: 'zonewise',
    projectName: 'ZoneWise.AI V2',
  },
};

// Load system prompt
const SYSTEM_PROMPT = readFileSync(
  join(__dirname, 'prompts/system.md'),
  'utf-8'
);

/**
 * Orchestrator Agent class
 */
export class OrchestratorAgent {
  private client: Anthropic;
  private metrics: SessionMetrics;
  private arcadeTools: any[] = [];

  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.metrics = this.initMetrics();
  }

  private initMetrics(): SessionMetrics {
    return {
      startTime: new Date(),
      tasksCompleted: 0,
      tasksFailed: 0,
      tasksBlocked: 0,
      tokensUsed: 0,
      delegations: [],
    };
  }

  /**
   * Initialize Arcade MCP tools
   */
  async initializeArcade(): Promise<void> {
    // TODO: Initialize Arcade MCP gateway
    // This will populate this.arcadeTools with Linear, GitHub, Slack tools
    console.log('Initializing Arcade MCP gateway...');
    
    // Placeholder - actual implementation will use Arcade SDK
    this.arcadeTools = [
      // Linear tools
      { name: 'linear_listIssues', description: 'List Linear issues' },
      { name: 'linear_updateIssue', description: 'Update a Linear issue' },
      { name: 'linear_createComment', description: 'Add comment to issue' },
      // GitHub tools
      { name: 'github_createPullRequest', description: 'Create a PR' },
      { name: 'github_mergePullRequest', description: 'Merge a PR' },
      // Slack tools
      { name: 'slack_postMessage', description: 'Post Slack message' },
    ];
  }

  /**
   * Read current state from Linear
   */
  async readLinearState(): Promise<LinearIssue[]> {
    console.log('Reading current state from Linear...');
    
    // TODO: Implement actual Linear API call via Arcade
    // For now, return mock data structure
    const issues: LinearIssue[] = [];
    
    // Actual implementation will use Arcade MCP:
    // const response = await this.callArcadeTool('linear_listIssues', {
    //   filter: { project: { name: { eq: CONFIG.linear.projectName } } }
    // });
    
    return issues;
  }

  /**
   * Identify highest priority tasks
   */
  prioritizeTasks(issues: LinearIssue[]): LinearIssue[] {
    return issues
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
        return 0;
      })
      .slice(0, CONFIG.limits.maxTasksPerSession);
  }

  /**
   * Determine which agent should handle a task
   */
  selectAgent(task: LinearIssue): string {
    const labels = task.labels.map(l => l.name);
    const title = task.title.toLowerCase();
    const desc = (task.description || '').toLowerCase();
    
    // Check for explicit agent labels
    if (labels.includes('agent:coding')) return 'coding';
    if (labels.includes('agent:linear')) return 'linear';
    if (labels.includes('agent:github')) return 'github';
    if (labels.includes('agent:slack')) return 'slack';
    
    // Infer from task content
    if (
      title.includes('implement') ||
      title.includes('create component') ||
      title.includes('fix bug') ||
      title.includes('refactor') ||
      desc.includes('write code')
    ) {
      return 'coding';
    }
    
    if (
      title.includes('create pr') ||
      title.includes('merge') ||
      title.includes('branch')
    ) {
      return 'github';
    }
    
    if (
      title.includes('notify') ||
      title.includes('update team') ||
      title.includes('post to slack')
    ) {
      return 'slack';
    }
    
    // Default to coding for implementation tasks
    return 'coding';
  }

  /**
   * Delegate task to appropriate sub-agent
   */
  async delegateTask(task: LinearIssue, agent: string): Promise<DelegationResult> {
    const startTime = Date.now();
    console.log(`Delegating task ${task.identifier} to ${agent} agent...`);
    
    try {
      // TODO: Implement actual delegation via Arcade MCP
      // Each sub-agent will have its own system prompt and tool set
      
      const result = await this.callSubAgent(agent, {
        taskId: task.identifier,
        title: task.title,
        description: task.description,
        acceptanceCriteria: this.extractAcceptanceCriteria(task),
      });
      
      return {
        success: true,
        agent,
        taskId: task.identifier,
        result,
        durationMs: Date.now() - startTime,
      };
    } catch (error: any) {
      return {
        success: false,
        agent,
        taskId: task.identifier,
        error: error.message,
        durationMs: Date.now() - startTime,
      };
    }
  }

  /**
   * Call a sub-agent with specific instructions
   */
  private async callSubAgent(agent: string, context: any): Promise<any> {
    const model = CONFIG.models[agent as keyof typeof CONFIG.models];
    
    // Load agent-specific system prompt
    const agentPromptPath = join(__dirname, '..', agent, 'prompts/system.md');
    let agentPrompt: string;
    try {
      agentPrompt = readFileSync(agentPromptPath, 'utf-8');
    } catch {
      agentPrompt = `You are the ${agent} agent for ZoneWise.AI. Complete the assigned task.`;
    }
    
    // TODO: Implement actual Claude API call with agent-specific tools
    // const response = await this.client.messages.create({
    //   model,
    //   max_tokens: 4096,
    //   system: agentPrompt,
    //   messages: [{ role: 'user', content: JSON.stringify(context) }],
    //   tools: this.getAgentTools(agent),
    // });
    
    return { status: 'completed', agent, context };
  }

  /**
   * Extract acceptance criteria from task description
   */
  private extractAcceptanceCriteria(task: LinearIssue): string[] {
    const desc = task.description || '';
    const criteria: string[] = [];
    
    // Parse markdown checklist items
    const matches = desc.matchAll(/- \[ \] (.+)/g);
    for (const match of matches) {
      criteria.push(match[1]);
    }
    
    return criteria;
  }

  /**
   * Update Linear with task result
   */
  async updateLinearStatus(
    taskId: string,
    success: boolean,
    summary: string
  ): Promise<void> {
    console.log(`Updating Linear issue ${taskId}...`);
    
    // TODO: Implement via Arcade MCP
    // await this.callArcadeTool('linear_updateIssue', {
    //   id: taskId,
    //   state: success ? 'Done' : 'Blocked',
    // });
    // await this.callArcadeTool('linear_createComment', {
    //   issueId: taskId,
    //   body: summary,
    // });
  }

  /**
   * Post session summary to Slack
   */
  async postSlackSummary(): Promise<void> {
    const duration = Math.round(
      (Date.now() - this.metrics.startTime.getTime()) / 60000
    );
    
    const summary = `
📊 *ZoneWise.AI Session Summary*
✅ Completed: ${this.metrics.tasksCompleted}
❌ Failed: ${this.metrics.tasksFailed}
⚠️ Blocked: ${this.metrics.tasksBlocked}
⏱️ Duration: ${duration} min
🔢 Tokens used: ${this.metrics.tokensUsed.toLocaleString()}
    `.trim();
    
    console.log('Posting session summary to Slack...');
    console.log(summary);
    
    // TODO: Implement via Arcade MCP
    // await this.callArcadeTool('slack_postMessage', {
    //   channel: '#zonewise-ai-updates',
    //   text: summary,
    // });
  }

  /**
   * Check if session should continue
   */
  shouldContinue(): boolean {
    const totalTasks = 
      this.metrics.tasksCompleted + 
      this.metrics.tasksFailed + 
      this.metrics.tasksBlocked;
    
    if (totalTasks >= CONFIG.limits.maxTasksPerSession) {
      console.log('Max tasks per session reached');
      return false;
    }
    
    if (this.metrics.tokensUsed >= CONFIG.limits.maxContextTokens) {
      console.log('Token budget exhausted');
      return false;
    }
    
    const elapsedMinutes = 
      (Date.now() - this.metrics.startTime.getTime()) / 60000;
    if (elapsedMinutes >= CONFIG.limits.timeoutMinutes) {
      console.log('Session timeout reached');
      return false;
    }
    
    return true;
  }

  /**
   * Main orchestration loop
   */
  async run(): Promise<void> {
    console.log('🚀 Starting ZoneWise.AI Orchestrator Session');
    console.log(`Time: ${new Date().toISOString()}`);
    
    try {
      // Initialize Arcade MCP
      await this.initializeArcade();
      
      // Read current state
      const issues = await this.readLinearState();
      console.log(`Found ${issues.length} issues in Linear`);
      
      // Prioritize tasks
      const prioritizedTasks = this.prioritizeTasks(issues);
      console.log(`Processing ${prioritizedTasks.length} prioritized tasks`);
      
      // Main delegation loop
      for (const task of prioritizedTasks) {
        if (!this.shouldContinue()) break;
        
        const agent = this.selectAgent(task);
        console.log(`\n--- Task: ${task.identifier} ---`);
        console.log(`Title: ${task.title}`);
        console.log(`Agent: ${agent}`);
        
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
            `❌ Failed: ${result.error}`
          );
        }
        
        // Checkpoint every N tasks
        const totalTasks = 
          this.metrics.tasksCompleted + 
          this.metrics.tasksFailed;
        if (totalTasks % CONFIG.limits.checkpointFrequency === 0) {
          console.log('Checkpointing progress...');
          // Linear is already updated, which serves as checkpoint
        }
      }
      
      // Post summary
      await this.postSlackSummary();
      
    } catch (error) {
      console.error('Session error:', error);
      throw error;
    }
    
    console.log('\n✅ Orchestrator session complete');
  }
}

// Main entry point
if (require.main === module) {
  const orchestrator = new OrchestratorAgent();
  orchestrator.run().catch(console.error);
}

export default OrchestratorAgent;
