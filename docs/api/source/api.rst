API Reference
=============

This section contains the complete API reference for nlp2mcp, organized by module.

Core Modules
------------

.. toctree::
   :maxdepth: 2

   api/ir
   api/ad
   api/kkt
   api/emit
   api/cli
   api/validation

Module Overview
---------------

**IR (Intermediate Representation)**
   Parse GAMS NLP models and build normalized intermediate representation

**AD (Automatic Differentiation)**
   Symbolic differentiation engine for computing gradients and Jacobians

**KKT (Karush-Kuhn-Tucker)**
   Assemble KKT optimality conditions from NLP model and derivatives

**Emit**
   Generate GAMS MCP code from KKT system

**CLI**
   Command-line interface for nlp2mcp tool

**Validation**
   PATH solver integration for validating generated MCP models
