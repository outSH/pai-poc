## Dev

### MySQL

docker run -p 3306:3306 -p 33060:33060 --name pai-poc-db -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:8.0.40

## Token

{
"alg": "RS256",
"kid": "1VEDiXkUYvihqg8drFe6t0AaHTIUQOoHkkxL8d7Q-4o",
"typ": "JWT"
}.{
"exp": 1729867989,
"nbf": 1729781589,
"ver": "1.0",
"iss": "https://fjresearchportal.b2clogin.com/c8d2f7a8-ca90-47a0-af8e-886d52c444f0/v2.0/",
"sub": "e4acb221-2238-48ac-9977-e863b702cfc2",
"aud": "7f96177c-fee7-42b9-a047-cd23d2ed8b3d",
"nonce": "defaultNonce",
"iat": 1729781589,
"auth_time": 1729781589,
"tid": "a19f121d-81e1-4858-a9d8-736e267fd4c7",
"oid": "e4acb221-2238-48ac-9977-e863b702cfc2",
"extension_user_id": "e4acb221-2238-48ac-9977-e863b702cfc2",
"extension_user_role": "user",
"extension_agent1_id": "sandbox001",
"extension_agent1_role": "administrator,tseal_user",
"extension_agent2_id": "gccAgentT1",
"extension_agent2_role": "administrator,tseal_user",
"extension_agent3_id": "paiAgentT1",
"extension_agent3_role": "administrator,tseal_user",
"extension_agent4_id": "sandbox004",
"extension_agent4_role": "administrator,tseal_user",
"domain": "fujitsu.com",
"tfp": "B2C_1A_SignIn_Username_Global"
}.[Signature]

# {

# "id": "670e674ad98d34b42567bb1a",

# "name": "gdc_pl_pai_poc"

# }

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
      "table_name": "periodic_processing_x1",
      "table_sync": true,
      "column": [
        {
          "name": "id",
          "type": "serial"
        },
        {
          "name": "uid",
          "type": "text"
        },
        {
          "name": "action",
          "type": "integer"
        },
        {
          "name": "eco_action_performed_at",
          "type": "timestamptz"
        },
        {
          "name": "quantity",
          "type": "integer"
        }
      ],
      "primary": ["id"],
      "unique": ["id"],
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
      "table_name": "periodic_processing_x1",
      "data": [
        [
          {
            "colname": "uid",
            "value": "1234-abcd-5678"
          },
          {
            "colname": "action",
            "value": 1
          },
          {
            "colname": "eco_action_performed_at",
            "value": "2022-11-17 13:31:31"
          },
          {
            "colname": "quantity",
            "value": 2
          }
        ]
      ]
    }
  ]
}
```

{
"result": "OK",
"detail": {
"message": "Success",
"process_id": 4729
}
}

### Get Data

- gccAgentT1
- paiAgentT1 (should fail before sending data: `Invalid Parameter.(bad param: table_name: table_depX1)`)

```json
{
  "target": [
    {
      "table_name": "periodic_processing_x1",
      "column_name": "id"
    },
    {
      "table_name": "periodic_processing_x1",
      "column_name": "uid"
    },
    {
      "table_name": "periodic_processing_x1",
      "column_name": "action"
    },
    {
      "table_name": "periodic_processing_x1",
      "column_name": "eco_action_performed_at"
    },
    {
      "table_name": "periodic_processing_x1",
      "column_name": "quantity"
    },
    {
      "table_name": "periodic_processing_x1",
      "column_name": "_system_sync_status"
    }
  ]
}
```

```json
{
  "target": [
    {
      "table_name": "periodic_processing_x1",
      "column_name": "id"
    }
  ],
  "where": {
    "sync_status": ["unsynchronized"]
  }
}
```

```json
{
  "target": [
    {
      "table_name": "periodic_processing_x1",
      "column_name": "id"
    }
  ],
  "where": {
    "sync_status": ["synchronized"],
    "sync_destination": ["paiAgentT1"]
  }
}
```

```json
{
  "target": [
    {
      "table_name": "periodic_processing_x1",
      "column_name": "id"
    }
  ],
  "where": {
    "condition": {
      "relation": "or",
      "exp": [
        {
          "table_name": "periodic_processing_x1",
          "column_name": "id",
          "operator": "=",
          "value": 1
        },
        {
          "table_name": "periodic_processing_x1",
          "column_name": "id",
          "operator": "=",
          "value": 3
        },
        {
          "table_name": "periodic_processing_x1",
          "column_name": "id",
          "operator": "=",
          "value": 2
        }
      ]
    },
    "sync_status": ["synchronized"],
    "sync_destination": ["paiAgentT1"]
  }
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
