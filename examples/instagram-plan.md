# Instagram comment-to-DM system

Colour = who does it: Coach, Coach's system, Stores, Instagram and followers. Solid: built and working. Dashed: the next build. Grey: later, not in this build. Yellow with a number: a guess; the number is the question that settles it.

## The simple version

```mermaid
flowchart TD
  subgraph band0["Coach's side"]
    coach["Coach<br/>takes over hot leads"]
  end
  subgraph band1["Coach's system, always on"]
    auto["Automation<br/>n8n workflow"]
    ai["AI agent<br/>answers DMs"]
  end
  subgraph band2["Stores"]
    contacts["Contacts table"]
    kb["Knowledge base"]
  end
  subgraph band3["Online"]
    ig["Instagram<br/>reels, comments, DMs"]
  end
  band0 ~~~ band1 ~~~ band2 ~~~ band3
  ig -->|"new comment"| auto
  auto -->|"checks, saves"| contacts
  ai -.->|"reads answers"| kb
  auto -.->|"DM question"| ai
  auto -->|"hot lead alert"| coach
  style coach fill:#dbeafe,stroke:#2563eb,color:#1e1e1e,stroke-width:2px
  style band0 fill:#f8fafc,stroke:#e2e8f0
  style auto fill:#ddd6fe,stroke:#6d28d9,color:#1e1e1e,stroke-width:2px
  style ai fill:#ddd6fe,stroke:#6d28d9,color:#1e1e1e,stroke-width:2px,stroke-dasharray:6 4
  style band1 fill:#f8fafc,stroke:#e2e8f0
  style contacts fill:#dcfce7,stroke:#16a34a,color:#1e1e1e,stroke-width:2px
  style kb fill:#dcfce7,stroke:#16a34a,color:#1e1e1e,stroke-width:2px,stroke-dasharray:6 4
  style band2 fill:#f8fafc,stroke:#e2e8f0
  style ig fill:#fed7aa,stroke:#c2410c,color:#1e1e1e,stroke-width:2px
  style band3 fill:#f8fafc,stroke:#e2e8f0
```

## Questions only the coach can answer

1. Which words make someone a hot lead?
2. May the system DM people who never commented?

## The full system, step by step

In the drawing `instagram-plan.excalidraw`, under the simple version.
