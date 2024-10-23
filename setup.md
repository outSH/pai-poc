## Setup

#### Create Agents

- `Trust-Agent-Id` to be configured beforehand:
  - gccAgentT1
  - paiAgentT1
- `user_id`: `e4acb221-2238-48ac-9977-e863b702cfc2`

```shell
# GCC Agent
{
    "agent_id": "gccAgentT1",
    "agent_name": "GCCAgent"
}

# PAI Agent
{
    "agent_id": "paiAgentT1",
    "agent_name": "PAIAgent"
}
```

#### Define

- gccAgentT1

```json
{
  "table_def": [
    {
      "table_name": "table_depX1",
      "table_sync": true,
      "column": [
        {
          "name": "dep_id",
          "type": "text"
        },
        {
          "name": "dep_name",
          "type": "text"
        },
        {
          "name": "dep_id1",
          "type": "text"
        },
        {
          "name": "dep_id2",
          "type": "text"
        }
      ],
      "primary": ["dep_id"],
      "unique": ["dep_id"],
      "sync_history": "on"
    }
  ]
}
```

### Register

- gccAgentT1

```json
{
  "register_type": "insert",
  "register_table": [
    {
      "table_name": "table_depX1",
      "data": [
        [
          {
            "colname": "dep_id",
            "value": "2"
          },
          {
            "colname": "dep_name",
            "value": "Registration information 1"
          },
          {
            "colname": "dep_id1",
            "value": "101"
          },
          {
            "colname": "dep_id2",
            "value": "asd"
          }
        ]
      ]
    }
  ]
}
```

### Get Data

- gccAgentT1
- paiAgentT1 (should fail before sending data: `Invalid Parameter.(bad param: table_name: table_depX1)`)

```json
{
  "target": [
    {
      "table_name": "table_depX1",
      "column_name": "dep_id"
    },
    {
      "table_name": "table_depX1",
      "column_name": "dep_name"
    },
    {
      "table_name": "table_depX1",
      "column_name": "_system_reg_agent_id"
    },
    {
      "table_name": "table_depX1",
      "column_name": "_system_sync_status"
    }
  ],
  "limit": 10
}
```

### Send Data

- gccAgentT1

```json
{
  "agent_id": ["paiAgentT1"],
  "data": [
    {
      "table_name": "table_depX1",
      "column": [
        {
          "name": "dep_id"
        },
        {
          "name": "dep_name"
        },
        {
          "name": "dep_id1"
        },
        {
          "name": "dep_id2"
        }
      ],
      "record": [
        {
          "key": [
            {
              "name": "dep_id",
              "value": "2"
            }
          ]
        }
      ]
    }
  ]
}
```
