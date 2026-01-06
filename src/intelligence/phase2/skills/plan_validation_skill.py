"""Plan Validation Skill for Phase 2 intelligence.

Verifies that an execution plan is sound, complete,
and executable before proceeding.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..skills.skill_interface import Skill, SkillError, SkillValidationError, SkillExecutionError
from ..phase2.data_models import ExecutionPlan, ValidationReport, ValidationIssue


class PlanValidationSkill(Skill):
    """Skill for validating execution plans.

    Validates plans for:
    - Completeness (all requirements addressed)
    - Dependency graph (no circular dependencies)
    - Command syntax (valid Phase 1 commands)
    - Risk assessment (dangerous operations)
    """

    @property
    def name(self) -> str:
        return "plan_validation_phase2"

    @property
    def description(self) -> str:
        return "Validates execution plans for soundness and completeness"

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_inputs(self, plan: ExecutionPlan, **kwargs: Any) -> None:
        """Validate inputs before execution."""
        if not plan or not plan.steps:
            raise SkillValidationError("plan must have at least one step")
        if len(plan.steps) > 1000:
            raise SkillValidationError("plan has too many steps (>1000)")

    def execute(
        self,
        context: Any,
        plan: ExecutionPlan,
        phase1_schema: Dict[str, Any] = None,
        current_state: Dict[str, Any] = None,
        validation_rules: List[Any] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate execution plan.

        Args:
            context: The current execution context.
            plan: Execution plan to validate.
            phase1_schema: Phase 1 command schema.
            current_state: Current task state (optional).
            validation_rules: Custom validation rules (optional).

        Returns:
            Dictionary containing ValidationReport data.

        Raises:
            SkillExecutionError: If validation fails catastrophically.
        """
        # Default Phase 1 schema if not provided
        if phase1_schema is None:
            phase1_schema = {
                "valid_commands": ["add", "list", "complete", "delete", "update", "help", "exit"],
                "command_patterns": {
                    "add": r"^add task[:\s]*(.+)$",
                    "list": r"^list tasks?$",
                    "complete": r"^complete[:\s]*(.+)$",
                    "delete": r"^delete[:\s]*(.+)$",
                    "update": r"^update[:\s]*(.+?)\s*to\s*(.+)$",
                    "help": r"^help$",
                    "exit": r"^(exit|quit|bye|goodbye)$"
                }
            }

        # Perform validation checks
        checks = []
        issues = []
        critical_issues = []
        warnings = []

        # Check 1: Completeness
        completeness_check = self._check_completeness(plan, validation_rules)
        checks.append(completeness_check)
        issues.extend([i for i in completeness_check["issues"] if i["severity"] == "HIGH"])
        warnings.extend([i for i in completeness_check["issues"] if i["severity"] == "MEDIUM" or i["severity"] == "LOW"])

        # Check 2: Dependencies
        dependency_check = self._check_dependencies(plan)
        checks.append(dependency_check)
        if dependency_check["status"] == "FAIL":
            critical_issues.extend(dependency_check["issues"])
        else:
            warnings.extend([i for i in dependency_check["issues"] if i["severity"] in ["MEDIUM", "LOW"]])

        # Check 3: Command syntax
        syntax_check = self._check_command_syntax(plan, phase1_schema)
        checks.append(syntax_check)
        if syntax_check["status"] == "FAIL":
            critical_issues.extend(syntax_check["issues"])
        else:
            warnings.extend([i for i in syntax_check["issues"] if i["severity"] in ["MEDIUM", "LOW"]])

        # Check 4: Risk assessment
        risk_check = self._check_risks(plan)
        checks.append(risk_check)
        if risk_check["status"] == "FAIL":
            critical_issues.extend(risk_check["issues"])
        else:
            warnings.extend([i for i in risk_check["issues"] if i["severity"] in ["MEDIUM", "LOW"]])

        # Calculate counts
        passed_checks = len([c for c in checks if c["status"] == "PASS"])
        failed_checks = len([c for c in checks if c["status"] == "FAIL"])
        warning_checks = len([c for c in checks if c["status"] == "WARN"])

        # Determine overall status
        if len(critical_issues) > 0:
            overall_status = "FAIL"
        elif len(warnings) > 0:
            overall_status = "WARN"
        else:
            overall_status = "PASS"

        # Calculate overall score
        overall_score = self._calculate_overall_score(checks)

        # Determine risk level
        risk_level = self._determine_risk_level(risk_check)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, warnings)

        return {
            "validation_report": ValidationReport(
                status=overall_status,
                overall_score=overall_score,
                is_executable=len(critical_issues) == 0,
                checks=checks,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warning_checks=warning_checks,
                issues=issues,
                critical_issues=critical_issues,
                warnings=warnings,
                risk_level=risk_level,
                recommendations=recommendations
            )
        }

    def _check_completeness(
        self,
        plan: ExecutionPlan,
        validation_rules: List[Any]
    ) -> Dict[str, Any]:
        """Check if plan addresses all requirements."""
        issues = []
        passed = True

        # Simple check: plan should have steps
        if not plan.steps:
            issues.append(ValidationIssue(
                issue_id="empty_plan",
                check_id="completeness",
                issue_type="MISSING_STEP",
                severity="HIGH",
                description="Plan has no steps",
                location="plan",
                suggestion="Add at least one step to plan",
                block_execution=True
            ))
            passed = False

        # Check for reasonable step count (at least 1 step)
        elif len(plan.steps) < 1:
            issues.append(ValidationIssue(
                issue_id="no_steps",
                check_id="completeness",
                issue_type="MISSING_STEP",
                severity="HIGH",
                description="Plan requires at least one executable step",
                location="plan",
                suggestion="Add steps to plan",
                block_execution=True
            ))

        return {
            "check_id": "completeness",
            "check_name": "Completeness Check",
            "check_type": "COMPLETENESS",
            "status": "FAIL" if not passed else "PASS",
            "message": "Plan contains executable steps" if passed else "Plan incomplete",
            "severity": "HIGH" if not passed else "LOW",
            "checked_at": self._get_timestamp(),
            "issues": issues
        }

    def _check_dependencies(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Check dependency graph for circular dependencies."""
        issues = []
        passed = True

        # Build dependency graph
        graph = {step.id: step.dependencies for step in plan.steps}

        # Detect cycles
        if self._has_cycle(graph):
            issues.append(ValidationIssue(
                issue_id="circular_dependency",
                check_id="dependency",
                issue_type="CIRCULAR_DEPENDENCY",
                severity="HIGH",
                description="Plan contains circular dependencies",
                location="dependency_graph",
                suggestion="Remove circular dependencies or reorder steps",
                block_execution=True
            ))
            passed = False

        # Check for isolated steps (no incoming edges)
        all_dependencies = set()
        for deps in graph.values():
            all_dependencies.update(deps)

        isolated = [step_id for step_id in graph.keys() if step_id not in all_dependencies and step_id != plan.steps[0].id]

        if isolated:
            for step_id in isolated:
                issues.append(ValidationIssue(
                    issue_id=f"isolated_step_{step_id}",
                    check_id="dependency",
                    issue_type="MISSING_STEP",
                    severity="MEDIUM",
                    description=f"Step {step_id} has no dependencies pointing to it",
                    location=step_id,
                    suggestion="Add missing dependency or remove isolated step",
                    block_execution=False
                ))

        return {
            "check_id": "dependency",
            "check_name": "Dependency Check",
            "check_type": "DEPENDENCY",
            "status": "FAIL" if not passed else "PASS",
            "message": "No circular dependencies" if passed else "Dependency issues found",
            "severity": "HIGH" if not passed else "LOW",
            "checked_at": self._get_timestamp(),
            "issues": issues
        }

    def _check_command_syntax(
        self,
        plan: ExecutionPlan,
        phase1_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if all plan steps have valid Phase 1 commands."""
        issues = []
        passed = True

        valid_commands = set(phase1_schema.get("valid_commands", []))
        command_patterns = phase1_schema.get("command_patterns", {})

        for step in plan.steps:
            command_type = step.command_type

            # Check if command type is valid
            if command_type not in valid_commands:
                issues.append(ValidationIssue(
                    issue_id=f"invalid_command_{step.id}",
                    check_id="syntax",
                    issue_type="INVALID_COMMAND",
                    severity="HIGH",
                    description=f"Step {step.id} uses invalid command type: {command_type}",
                    location=step.id,
                    suggestion=f"Use valid command: {', '.join(valid_commands)}",
                    block_execution=True
                ))
                passed = False

            # Check command syntax against patterns
            elif command_type in command_patterns:
                pattern = command_patterns[command_type]
                import re
                if not re.match(pattern, step.command, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        issue_id=f"syntax_error_{step.id}",
                        check_id="syntax",
                        issue_type="INVALID_COMMAND",
                        severity="MEDIUM",
                        description=f"Step {step.id} command syntax doesn't match expected pattern",
                        location=step.id,
                        suggestion=f"Match pattern: {pattern}",
                        block_execution=False
                    ))

        return {
            "check_id": "syntax",
            "check_name": "Syntax Check",
            "check_type": "SYNTAX",
            "status": "FAIL" if not passed else "PASS",
            "message": "All commands valid" if passed else "Command syntax issues detected",
            "severity": "HIGH" if not passed else "LOW",
            "checked_at": self._get_timestamp(),
            "issues": issues
        }

    def _check_risks(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Assess risk factors in plan."""
        issues = []
        passed = True
        risk_factors = []

        # Check for high-risk operations
        for step in plan.steps:
            # Check for delete operations (higher risk)
            if step.command_type == "DELETE" and step.priority == "P1":
                risk_factors.append(f"High-priority delete operation: {step.id}")
                issues.append(ValidationIssue(
                    issue_id=f"risky_delete_{step.id}",
                    check_id="risk",
                    issue_type="RISK",
                    severity="MEDIUM",
                    description=f"Step {step.id} is a high-priority delete operation",
                    location=step.id,
                    suggestion="Consider backing up data or confirming with user",
                    block_execution=False
                ))

            # Check for bulk operations
            if len(plan.steps) > 10 and step.priority == "P1":
                risk_factors.append("Bulk operation plan")
                issues.append(ValidationIssue(
                    issue_id="bulk_operations",
                    check_id="risk",
                    issue_type="RISK",
                    severity="LOW",
                    description="Plan involves many operations",
                    location="plan",
                    suggestion="Consider breaking into smaller plans",
                    block_execution=False
                ))

        return {
            "check_id": "risk",
            "check_name": "Risk Assessment",
            "check_type": "RISK",
            "status": "FAIL" if len(risk_factors) > 0 else "PASS",
            "message": "No high-risk operations" if len(risk_factors) == 0 else f"Risk factors: {', '.join(risk_factors)}",
            "severity": "MEDIUM" if len(risk_factors) > 0 else "LOW",
            "checked_at": self._get_timestamp(),
            "issues": issues
        }

    def _has_cycle(self, graph: Dict[str, List[str]]) -> bool:
        """Detect if dependency graph has circular dependencies."""
        visited = set()
        recursion_stack = set()

        def visit(node: str) -> bool:
            if node in recursion_stack:
                return True  # Cycle found
            if node in visited:
                return False

            visited.add(node)
            recursion_stack.add(node)

            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True

            recursion_stack.remove(node)
            return False

        # Check all nodes
        for node in graph:
            if visit(node):
                return True

        return False

    def _calculate_overall_score(self, checks: List[Any]) -> float:
        """Calculate overall quality score from validation checks."""
        if not checks:
            return 0.5

        total_score = 0.0
        weight_sum = 0.0

        for check in checks:
            status = check.get("status", "PASS")
            severity = check.get("severity", "LOW")

            # Weight by status
            if status == "PASS":
                status_weight = 1.0
            elif status == "FAIL":
                status_weight = -1.0
            else:  # WARN
                status_weight = -0.2

            # Weight by severity
            severity_weight = {
                "HIGH": 1.0,
                "MEDIUM": 0.6,
                "LOW": 0.3
            }.get(severity, 0.5)

            weight_sum += severity_weight
            total_score += status_weight * severity_weight

        # Normalize to 0.0-1.0 range
        if weight_sum > 0:
            normalized = (total_score / weight_sum + 1.0) / 2.0 + 0.5
            return max(0.0, min(1.0, normalized))
        return 0.5

    def _determine_risk_level(self, risk_check: Dict[str, Any]) -> str:
        """Determine overall risk level."""
        if risk_check["status"] == "FAIL" and risk_check["severity"] == "HIGH":
            return "HIGH"
        elif risk_check["status"] == "FAIL":
            return "MEDIUM"
        elif risk_check["status"] == "WARN":
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(self, issues: List[ValidationIssue], warnings: List[ValidationIssue]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if not issues and not warnings:
            return ["Plan validated successfully - no issues found"]

        # Add recommendations for critical issues
        for issue in issues:
            if issue.block_execution:
                recommendations.append(f"Fix before execution: {issue.suggestion}")

        # Add recommendations for warnings
        for warning in warnings:
            recommendations.append(f"Consider: {warning.suggestion}")

        return list(set(recommendations))

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
