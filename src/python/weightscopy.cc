#include "weightscopy.h"

namespace lczero {
namespace rust {

extern "C" {

std::string uci_from_rustmove(RustMove move) {
  char from_row = '1' + (move.from / 8);
  char from_col = 'a' + (move.from % 8);
  char to_row = '1' + (move.to / 8);
  char to_col = 'a' + (move.to % 8);
  char uci[] = {from_col, from_row, to_col, to_row, move.promotion, '\0'};
  return std::string(uci);
}

std::unique_ptr<Input> input_from_rust_request(
    const Backend* b, const RustEvaluationRequest* request) {
  std::vector<std::string> uci_history = std::vector<std::string>();
  for (size_t i = 0; i < request->history.length; ++i) {
    RustMove move = request->history.moves[i];
    std::string uci = uci_from_rustmove(move);
    uci_history.push_back(uci);
  }
  GameState g = GameState(std::string(request->starting_fen), uci_history);
  std::unique_ptr<Input> input = g.as_input(*b);
  return input;
}

uint16_t move_to_policy_index(RustMove m, bool black) {
  lczero::Move lczero_move = lczero::Move(uci_from_rustmove(m), black);
  return lczero_move.as_nn_index(0);
}

RustBackend* new_backend(const char* str) {
  Weights w = Weights(str);
  Backend* b = new Backend(&w, std::nullopt, std::nullopt);
  return (RustBackend*)b;
}

RustEvaluation* evaluate(const RustBackend* t,
                         const RustEvaluationRequest* requests,
                         size_t num_requests) {
  Backend* b = (Backend*)t;

  std::vector<std::unique_ptr<Input>> inputs;
  std::vector<Input*> input_pointers;
  for (size_t i = 0; i < num_requests; ++i) {
    auto inp = input_from_rust_request(b, &(requests[i]));
    input_pointers.push_back(inp.get());
    inputs.push_back(std::move(inp));
  }
  std::vector<std::unique_ptr<Output>> o = b->evaluate(input_pointers);
  RustEvaluation* response = new RustEvaluation[o.size()];
  for (size_t i = 0; i < o.size(); ++i) {
    response[i].q_ = o[i]->q_;
    response[i].d_ = o[i]->d_;
    response[i].m_ = o[i]->m_;
    std::copy(std::begin(o[i]->p_), std::end(o[i]->p_),
              std::begin(response[i].p_));
  }
  return response;
}

void delete_backend(RustBackend* t) {
  Backend* b = (Backend*)t;
  delete b;
}
}
}  // namespace rust
}  // namespace lczero