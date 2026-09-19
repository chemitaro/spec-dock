# Runtime coordination

This directory holds runtime coordination data. `create.lock` serializes `create` and `import` operations while the repository shared lease is held. It does not define candidate identity or lifecycle authority; those remain bound to the current repository state.
