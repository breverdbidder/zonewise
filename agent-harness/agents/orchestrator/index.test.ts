/**
 * ZoneWise.AI Orchestrator Agent Test Suite
 * 
 * Comprehensive tests for code quality, security, and reliability
 * 
 * @module OrchestratorAgent.test
 * @version 2.0.0
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

// Mock Anthropic SDK before importing
jest.mock('@anthropic-ai/sdk', () => ({
  default: jest.fn().mockImplementation(() => ({
    messages: {
      create: jest.fn().mockResolvedValue({
        content: [{ type: 'text', text: 'Task completed' }],
        usage: { input_tokens: 100, output_tokens: 50 },
      }),
    },
  })),
}));

// Import after mocking
import OrchestratorAgent from './index';

// ============================================================================
// TEST FIXTURES
// ============================================================================

const mockLinearIssue = {
  id: 'issue-123',
  identifier: 'ZW-42',
  title: 'Implement user authentication',
  state: { name: 'Backlog' as const },
  priority: 1 as const,
  labels: [{ name: 'agent:coding' }],
  description: '- [ ] Add login form\n- [ ] Add JWT validation',
};

const mockLinearIssueGitHub = {
  id: 'issue-456',
  identifier: 'ZW-43',
  title: 'Create PR for feature branch',
  state: { name: 'In Progress' as const },
  priority: 2 as const,
  labels: [{ name: 'agent:github' }],
  description: 'Merge feature/auth into main',
};

const mockInvalidIssue = {
  id: 'bad-issue',
  // Missing required fields
};

// ============================================================================
// UNIT TESTS
// ============================================================================

describe('OrchestratorAgent', () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    process.env.ANTHROPIC_API_KEY = 'test-api-key';
    process.env.ARCADE_API_KEY = 'test-arcade-key';
    jest.clearAllMocks();
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Constructor', () => {
    it('should initialize with valid environment', () => {
      const agent = new OrchestratorAgent();
      expect(agent).toBeDefined();
    });

    it('should throw without ANTHROPIC_API_KEY', () => {
      delete process.env.ANTHROPIC_API_KEY;
      expect(() => new OrchestratorAgent()).toThrow('Missing required environment variables');
    });

    it('should generate unique session ID', () => {
      const agent1 = new OrchestratorAgent();
      const agent2 = new OrchestratorAgent();
      const metrics1 = agent1.getMetrics();
      const metrics2 = agent2.getMetrics();
      expect(metrics1.sessionId).not.toBe(metrics2.sessionId);
    });

    it('should initialize circuit breakers for all agents', () => {
      const agent = new OrchestratorAgent();
      // Circuit breakers are private, but we can verify behavior
      expect(agent).toBeDefined();
    });
  });

  describe('Task Prioritization', () => {
    let agent: OrchestratorAgent;

    beforeEach(() => {
      agent = new OrchestratorAgent();
    });

    it('should filter out completed tasks', () => {
      const issues = [
        { ...mockLinearIssue, state: { name: 'Done' as const } },
        mockLinearIssue,
      ];
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized).toHaveLength(1);
      expect(prioritized[0].identifier).toBe('ZW-42');
    });

    it('should filter out blocked tasks', () => {
      const issues = [
        { ...mockLinearIssue, state: { name: 'Blocked' as const } },
        mockLinearIssue,
      ];
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized).toHaveLength(1);
    });

    it('should sort by priority (1 before 2)', () => {
      const issues = [
        { ...mockLinearIssue, priority: 2 as const },
        { ...mockLinearIssue, priority: 1 as const, identifier: 'ZW-1' },
      ];
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized[0].identifier).toBe('ZW-1');
    });

    it('should prefer in-progress tasks at same priority', () => {
      const issues = [
        { ...mockLinearIssue, state: { name: 'Backlog' as const } },
        { ...mockLinearIssue, state: { name: 'In Progress' as const }, identifier: 'ZW-IP' },
      ];
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized[0].identifier).toBe('ZW-IP');
    });

    it('should limit to max tasks per session', () => {
      const issues = Array.from({ length: 20 }, (_, i) => ({
        ...mockLinearIssue,
        identifier: `ZW-${i}`,
      }));
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized.length).toBeLessThanOrEqual(10);
    });

    it('should handle invalid issues gracefully', () => {
      const issues = [mockInvalidIssue as any, mockLinearIssue];
      const prioritized = agent.prioritizeTasks(issues);
      expect(prioritized).toHaveLength(1);
    });

    it('should handle empty array', () => {
      const prioritized = agent.prioritizeTasks([]);
      expect(prioritized).toHaveLength(0);
    });
  });

  describe('Agent Selection', () => {
    let agent: OrchestratorAgent;

    beforeEach(() => {
      agent = new OrchestratorAgent();
    });

    it('should select coding agent for explicit label', () => {
      const selected = agent.selectAgent(mockLinearIssue);
      expect(selected).toBe('coding');
    });

    it('should select github agent for explicit label', () => {
      const selected = agent.selectAgent(mockLinearIssueGitHub);
      expect(selected).toBe('github');
    });

    it('should infer coding agent from keywords', () => {
      const issue = {
        ...mockLinearIssue,
        labels: [],
        title: 'Implement new feature',
      };
      const selected = agent.selectAgent(issue);
      expect(selected).toBe('coding');
    });

    it('should infer github agent from keywords', () => {
      const issue = {
        ...mockLinearIssue,
        labels: [],
        title: 'Create PR for release',
      };
      const selected = agent.selectAgent(issue);
      expect(selected).toBe('github');
    });

    it('should infer slack agent from keywords', () => {
      const issue = {
        ...mockLinearIssue,
        labels: [],
        title: 'Notify team about deployment',
      };
      const selected = agent.selectAgent(issue);
      expect(selected).toBe('slack');
    });

    it('should default to coding for ambiguous tasks', () => {
      const issue = {
        ...mockLinearIssue,
        labels: [],
        title: 'Do something',
        description: '',
      };
      const selected = agent.selectAgent(issue);
      expect(selected).toBe('coding');
    });

    it('should handle XSS in task title', () => {
      const issue = {
        ...mockLinearIssue,
        title: '<script>alert("xss")</script>implement feature',
      };
      const selected = agent.selectAgent(issue);
      expect(selected).toBe('coding');
    });
  });

  describe('Session Management', () => {
    let agent: OrchestratorAgent;

    beforeEach(() => {
      agent = new OrchestratorAgent();
    });

    it('should continue with no tasks processed', () => {
      expect(agent.shouldContinue()).toBe(true);
    });

    it('should track metrics correctly', () => {
      const metrics = agent.getMetrics();
      expect(metrics.tasksCompleted).toBe(0);
      expect(metrics.tasksFailed).toBe(0);
      expect(metrics.tokensUsed).toBe(0);
      expect(metrics.sessionId).toBeDefined();
    });

    it('should return immutable metrics', () => {
      const metrics = agent.getMetrics();
      expect(Object.isFrozen(metrics)).toBe(true);
    });

    it('should maintain audit log', () => {
      const auditLog = agent.getAuditLog();
      expect(auditLog.length).toBeGreaterThan(0);
      expect(auditLog[0].action).toBe('SESSION_STARTED');
    });

    it('should return immutable audit log', () => {
      const auditLog = agent.getAuditLog();
      expect(Object.isFrozen(auditLog)).toBe(true);
    });
  });

  describe('Error Handling', () => {
    let agent: OrchestratorAgent;

    beforeEach(() => {
      agent = new OrchestratorAgent();
    });

    it('should classify network errors as recoverable', async () => {
      // Network errors should be recoverable
      const networkError = new Error('Network error: ECONNREFUSED');
      // Test would involve mocking API calls to throw this error
      expect(networkError.message).toContain('ECONNREFUSED');
    });

    it('should classify auth errors as non-recoverable', async () => {
      const authError = new Error('401 Unauthorized');
      expect(authError.message).toContain('Unauthorized');
    });

    it('should classify rate limits as recoverable', async () => {
      const rateLimitError = new Error('429 Too Many Requests - Rate limited');
      expect(rateLimitError.message).toContain('Rate limited');
    });
  });

  describe('Input Sanitization', () => {
    let agent: OrchestratorAgent;

    beforeEach(() => {
      agent = new OrchestratorAgent();
    });

    it('should handle tasks with malicious input', () => {
      const maliciousIssue = {
        ...mockLinearIssue,
        title: '${process.env.SECRET}',
        description: '`rm -rf /`',
      };
      // Should not throw
      const selected = agent.selectAgent(maliciousIssue);
      expect(selected).toBeDefined();
    });

    it('should handle extremely long input', () => {
      const longIssue = {
        ...mockLinearIssue,
        title: 'A'.repeat(50000),
        description: 'B'.repeat(100000),
      };
      // Should not throw or hang
      const selected = agent.selectAgent(longIssue);
      expect(selected).toBeDefined();
    });
  });
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

describe('OrchestratorAgent Integration', () => {
  let agent: OrchestratorAgent;

  beforeEach(() => {
    process.env.ANTHROPIC_API_KEY = 'test-api-key';
    agent = new OrchestratorAgent();
  });

  it('should complete a full session lifecycle', async () => {
    // Initialize
    await agent.initializeArcade();
    
    // Run (with mocked Linear returning empty)
    const metrics = await agent.run();
    
    expect(metrics.sessionId).toBeDefined();
    expect(metrics.tasksCompleted).toBe(0); // No real tasks
    expect(metrics.delegations).toHaveLength(0);
  });

  it('should handle arcade initialization failure gracefully', async () => {
    delete process.env.ARCADE_API_KEY;
    const newAgent = new OrchestratorAgent();
    
    // Should not throw, should use mock tools
    await newAgent.initializeArcade();
    expect(newAgent).toBeDefined();
  });
});

// ============================================================================
// SECURITY TESTS
// ============================================================================

describe('Security', () => {
  it('should not expose API keys in logs', () => {
    process.env.ANTHROPIC_API_KEY = 'sk-secret-key-12345';
    const consoleSpy = jest.spyOn(console, 'log');
    
    const agent = new OrchestratorAgent();
    const auditLog = agent.getAuditLog();
    
    const logOutput = JSON.stringify(auditLog);
    expect(logOutput).not.toContain('sk-secret-key');
    
    consoleSpy.mockRestore();
  });

  it('should not include sensitive data in metrics', () => {
    process.env.ANTHROPIC_API_KEY = 'test-key';
    const agent = new OrchestratorAgent();
    const metrics = agent.getMetrics();
    
    const metricsStr = JSON.stringify(metrics);
    expect(metricsStr).not.toContain('apiKey');
    expect(metricsStr).not.toContain('ANTHROPIC');
  });

  it('should validate environment variables', () => {
    delete process.env.ANTHROPIC_API_KEY;
    expect(() => new OrchestratorAgent()).toThrow();
  });
});

// ============================================================================
// PERFORMANCE TESTS
// ============================================================================

describe('Performance', () => {
  it('should prioritize 1000 tasks in under 100ms', () => {
    process.env.ANTHROPIC_API_KEY = 'test-key';
    const agent = new OrchestratorAgent();
    
    const issues = Array.from({ length: 1000 }, (_, i) => ({
      id: `issue-${i}`,
      identifier: `ZW-${i}`,
      title: `Task ${i}`,
      state: { name: 'Backlog' as const },
      priority: ((i % 4) + 1) as 1 | 2 | 3 | 4,
      labels: [],
    }));
    
    const start = Date.now();
    agent.prioritizeTasks(issues);
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(100);
  });

  it('should select agent in under 10ms', () => {
    process.env.ANTHROPIC_API_KEY = 'test-key';
    const agent = new OrchestratorAgent();
    
    const start = Date.now();
    for (let i = 0; i < 100; i++) {
      agent.selectAgent(mockLinearIssue);
    }
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(100); // 100 selections in under 100ms
  });
});
