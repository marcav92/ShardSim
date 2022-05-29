# protocols
BASIC_RIVET = "BASIC_RIVET"


# shard types
WORKER = "WORKER"
REFERENCE = "REFERENCE"

# Event Types
# Client
EVT_SEND_TRANSACTION = "SEND_TRANSACTION"

# Layer 1
EVT_RECEIVE_TRANSACTION = "RECEIVE_TRANSACTION"


# layer 2
EVT_WORKER_CREATE_BLOCK = "WORKER_CREATE_BLOCK"
EVT_REFERENCE_CREATE_BLOCK = "REFERENCE_CREATE_BLOCK"
EVT_WORKER_VERIFY_BLOCK = "WORKER_VERIFY_BLOCK"
EVT_REFERENCE_VERIFY_BLOCK = "REFERENCE_VERIFY_BLOCK"


# hot stuff phases
PREPARE = "PREPARE"
PRECOMMIT = "PRECOMMIT"
COMMIT = "COMMIT"
DECIDE = "DECIDE"

# #layer 2 hotstuff generic
EVT_REFERENCE_HOT_STUFF_MESSAGE = "REFERENCE_HOT_STUFF_MESSAGE"
EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE = "REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE"
EVT_REFERENCE_HOT_STUFF_PREPARE_MESSAGE = "REFERENCE_HOT_STUFF_PREPARE_MESSAGE"
EVT_REFERENCE_HOT_STUFF_PREPARE_VOTE_MESSAGE = "REFERENCE_HOT_STUFF_PREPARE_VOTE_MESSAGE"
EVT_REFERENCE_HOT_STUFF_PRECOMMIT_MESSAGE = "REFERENCE_HOT_STUFF_PRECOMMIT_MESSAGE"
EVT_REFERENCE_HOT_STUFF_PRECOMMIT_VOTE_MESSAGE = "REFERENCE_HOT_STUFF_PRECOMMIT_VOTE_MESSAGE"
EVT_REFERENCE_HOT_STUFF_COMMIT_MESSAGE = "REFERENCE_HOT_STUFF_COMMIT_MESSAGE"
EVT_REFERENCE_HOT_STUFF_COMMIT_VOTE_MESSAGE = "REFERENCE_HOT_STUFF_COMMIT_VOTE_MESSAGE"
EVT_REFERENCE_HOT_STUFF_DECIDE_MESSAGE = "REFERENCE_HOT_STUFF_DECIDE_MESSAGE"
EVT_REFERENCE_HOT_STUFF_NEXT_VIEW_INTERRUPT = "REFERENCE_HOT_STUFF_NEXT_VIEW_INTERRUPT"

# rivet delay_types
INTRA_SHARD_DELAY = "INTRA_SHARD_DELAY"
WORKER_REFERENCE_COMM_DELAY = "WORKER_REFERENCE_COMM_DELAY"

# rivet reference phases
PREPARE = "PREPARE"
PRECOMMIT = "PRECOMMIT"
COMMIT = "COMMIT"
DECIDE = "DECIDE"

# rivet worker phases
PROPOSAL = "PROPOSAL"
CERTIFICATION = "CERTIFICATION"

# layer 2 rivet reference events
EVT_REFERENCE_RIVET_MESSAGE = "REFERENCE_RIVET_MESSAGE"
EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE = "REFERENCE_RIVET_NEW_VIEW_MESSAGE"
EVT_REFERENCE_RIVET_PREPARE_MESSAGE = "REFERENCE_RIVET_PREPARE_MESSAGE"
EVT_REFERENCE_RIVET_PREPARE_VOTE_MESSAGE = "REFERENCE_RIVET_PREPARE_VOTE_MESSAGE"
EVT_REFERENCE_RIVET_PRECOMMIT_MESSAGE = "REFERENCE_RIVET_PRECOMMIT_MESSAGE"
EVT_REFERENCE_RIVET_PRECOMMIT_VOTE_MESSAGE = "REFERENCE_RIVET_PRECOMMIT_VOTE_MESSAGE"
EVT_REFERENCE_RIVET_COMMIT_MESSAGE = "REFERENCE_RIVET_COMMIT_MESSAGE"
EVT_REFERENCE_RIVET_COMMIT_VOTE_MESSAGE = "REFERENCE_RIVET_COMMIT_VOTE_MESSAGE"
EVT_REFERENCE_RIVET_DECIDE_MESSAGE = "REFERENCE_RIVET_DECIDE_MESSAGE"
EVT_REFERENCE_RIVET_NEXT_VIEW_INTERRUPT = "REFERENCE_RIVET_NEXT_VIEW_INTERRUPT"
EVT_REFERENCE_DATA_REQUEST = "EVT_REFERENCE_DATA_REQUEST"


# layer 2 rivet worker events
EVT_WORKER_RIVET_PROPOSAL_MESSAGE = "WORKER_RIVET_PROPOSAL_MESSAGE"
EVT_WORKER_RIVET_CERTIFICATION_MESSAGE = "WORKER_RIVET_CERTIFICATION_MESSAGE"
EVT_WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE = "WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE"
