// Derived from Verilator example: https://github.com/verilator/verilator/blob/master/examples/make_tracing_c/sim_main.cpp
// Original file was released under CC0 (public domain) by original author Wilson Snyder

// For std::unique_ptr
#include <memory>
// Output stuff
#include <cstdio>
#include <iostream>
#include <string>
#include <bitset>
#include <sstream>

#include <array>
#include <unordered_map>
#include <vector>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vtop.h"

// Legacy function required only so linking works on Cygwin and MSVC++
// TODO: remove if I decide to only support running in Linux container [pretty likely]
double sc_time_stamp() { return 0; }

//Communication protocol: strings of name,state
//State is 16 ASCII 1/0
//Name is variable length matching these names:

    /* ports
        input                UB
        input                DB
        input                LB
        input                RB
        input                CB
        input [15:0]         switches

        output [6:0]         segment
        output               dp
        output [3:0]         anode
        output [15:0]        lights
    */

/*
    Each loop, each outputitem's update function is called.
    If it returns a value, that means the output it wraps has changed,
    and the new state should be sent to client (i.e. printed to stdout)
*/
class OutputItem {
    private:
        unsigned int* read_source;
        int width;

        unsigned int value;
        int mask;
    public:
        std::string name;
        // Returns boolean for if the state has changed, and an int of current state
        std::pair<bool, int> poll() {
            unsigned int new_value = *(this->read_source) & mask;
            bool anything_new = (value != new_value);
            value = new_value;
            return std::pair<bool, int>(anything_new, value);
        }

        OutputItem(unsigned int* read_source, const std::string& name, int width) {
            this->read_source = read_source;
            this->width = width;
            this->mask = 0;
            
            for(int i = 0; i < this->width; i++) {
                this->mask <<= 1;
            	this->mask |= 1;
            }
            
            this->name = name;

            this->value = 1300;
        }
};

std::vector<std::string> split_string(const std::string& input_string, const char* separator) {
    std::vector<std::string> result = {};
    std::string segment = input_string;

    while(true) {
        auto next_sep = segment.find(*separator);
        if(next_sep != std::string::npos) { // At least one segment left
            result.push_back(segment.substr(0, next_sep));
            if(next_sep + 1 < segment.length()) { // There is stuff after segment, so continue loop
                segment = segment.substr(next_sep + 1);
            }
            else { // this was the last segment, followed by a separator with nothing after it
                break;
            }
        }
        else { // No more separators. Just put rest of string in last spot
            result.push_back(segment);
            break;
        }
    }

    return result;
}


std::pair<std::string, std::string> split_at_comma(const std::string& input) {
    auto comma_index = input.find(",");
    return std::pair<std::string, std::string>(input.substr(0, comma_index), input.substr(comma_index + 1));
}


std::unordered_map<std::string, int> py_string_to_map(const std::string& input) {
    // Converts a Python str() representation of a string:string dict to a map
    // Example input: "{'key_1': 14, 'key_2': 2}"

    std::unordered_map<std::string, int> output = {};

    // Get rid of the outer curly brackets: "'key_1': 14, 'key_2': 2}"
    auto trimmed_input = input.substr(1, input.length() - 2);

    // Vector of {"'key1': 14", " 'key_2': 2"} 
                              // ^ Note leading spaces after index 0
    auto keyval_strings = split_string(trimmed_input, ",");

    size_t index = 0;

    for(std::string keyval : keyval_strings) {
        if(index > 0) {
            keyval = keyval.substr(1); // Trim leading space
        }

        // Vector of {"'key1'", " 14"}
        std::vector<std::string> split = split_string(keyval, ":");

        std::string key = split[0];
        key = key.substr(1, key.length() - 2); // chop off single quotes
        int val = stoi(split[1]); // stoi discards whitespace automatically

        output[key] = val;

        index ++;
    }

    return output;
}

// From an input string updates the relevant component
void update_input(const std::string& input_string, Vtop* top) {
    auto [name, state_str] = split_at_comma(input_string);
    int state = stoi(state_str, nullptr, 2); // bitstring to int

    if(name == "UB") {
        top->UB = state;
    }
    else if(name == "DB") {
        top->DB = state;
    }
    else if(name == "LB") {
        top->LB = state;
    }
    else if(name == "RB") {
        top->RB = state;
    }
    else if(name == "CB") {
        top->CB = state;
    }
    else if(name == "switches") {
        top->switches = state;
    }
}


void parse_and_update_input(const std::string& input_string, Vtop* top) {
    auto update_dict = py_string_to_map(input_string);
    auto parts = split_string(input_string, "|");

    for(auto i : parts) {
        //std::cout << i;
        update_input(i, top);
    }
}

void update_from_key_val(std::string key, int val, Vtop* top) {
    if(key == "UB") {
        top->UB = val;
    }
    else if(key == "DB") {
        top->DB = val;
    }
    else if(key == "LB") {
        top->LB = val;
    }
    else if(key == "RB") {
        top->RB = val;
    }
    else if(key == "CB") {
        top->CB = val;
    }
    else if(key == "Switches") {
        top->switches = val;
    }
    else {
        std::cout << "Bad key: " << key << " (Val is " << val << ")" << std::endl;
    }
}

void update_inputs(const std::string& input_string, Vtop* top) {
    auto update_dict = py_string_to_map(input_string);

    for(auto i : update_dict) {
        auto key = i.first;
        auto val = i.second;

        update_from_key_val(key, val, top);
    }
}

std::string map_to_py_string(std::unordered_map<std::string, int> dict) {
    std::stringstream py_string_stream;

    bool inserted_one = false;
    for(auto i : dict) {
        if(inserted_one) { // Comma before entries after first
            py_string_stream << ", ";
        }
        else {
            inserted_one = true;
        }

        auto key = i.first;
        auto val = i.second;

        std::stringstream key_val_stream;
        key_val_stream << "'" << key << "': " << val;

        py_string_stream << key_val_stream.str();
    }

    return "{" + py_string_stream.str() + "}";
}

int main(int argc, char** argv) {
    // This is a more complicated example, please also see the simpler examples/make_hello_c.

    // Create logs/ directory in case we have traces to put under it
    Verilated::mkdir("logs");

    // Construct a VerilatedContext to hold simulation time, etc.
    // Multiple modules (made later below with Vtop) may share the same
    // context to share time, or modules may have different contexts if
    // they should be independent from each other.

    // Using unique_ptr is similar to
    // "VerilatedContext* contextp = new VerilatedContext" then deleting at end.
    const std::unique_ptr<VerilatedContext> contextp{new VerilatedContext};
    // Do not instead make Vtop as a file-scope static variable, as the
    // "C++ static initialization order fiasco" may cause a crash

    // Set debug level, 0 is off, 9 is highest presently used
    // May be overridden by commandArgs argument parsing
    contextp->debug(0);

    // Randomization reset policy
    // May be overridden by commandArgs argument parsing
    contextp->randReset(2);

    // Verilator must compute traced signals
    contextp->traceEverOn(false);

    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    contextp->commandArgs(argc, argv);

    // Construct the Verilated model, from Vtop.h generated from Verilating "top.v".
    // Using unique_ptr is similar to "Vtop* top = new Vtop" then deleting at end.
    // "TOP" will be the hierarchical name of the module.
    const std::unique_ptr<Vtop> top{new Vtop{contextp.get(), "TOP"}};

    // Initialize Vtop's input signals all to 0
    top->clk = 0;

    top->UB = 0;
    top->DB = 0;
    top->LB = 0;
    top->RB = 0;
    top->CB = 0;
    
    top->switches = 0;

    std::string input;

    std::array<OutputItem, 4> outputs_array = {
        OutputItem ((unsigned int*) &(top->segment), "Segment", 7),
        OutputItem ((unsigned int*) &(top->dp), "DP", 1),
        OutputItem ((unsigned int*) &(top->anode), "Anode", 4),
        OutputItem ((unsigned int*) &(top->lights), "Lights", 16)
    };


    while (1) {
        getline(std::cin, input);
        if(input.find("exit") != std::string::npos) {
            break;
        }
        else if(input.empty()) {
            // No new input sent
        }
        else {
            update_inputs(input, top.get()); // .get() to access inner pointer
            //std::cerr << "received " << input << std::endl;
        }

        top->clk = !(top->clk); // Flip clock

        contextp->timeInc(1);  // Advance one time unit
        top->eval(); // and run one frame of the model

        bool need_to_send = false;

        std::unordered_map<std::string, int> output_map = {};

        for(auto &i : outputs_array) {
            auto [anything_new, state] = i.poll();
            need_to_send |= anything_new;
            
            output_map[i.name] = state;
        }

        if(need_to_send) {
            std::cout << "secretkey" << map_to_py_string(output_map) << std::endl; // flush necessary for Python subprocess pipe
           // std::cerr << "sending " << map_to_py_string(output_map) << std::endl;
        }
        else {
           std::cout << "secretkey" << std::endl;
        }

    }

    // Final model cleanup
    top->final();

    // Final simulation summary
    contextp->statsPrintSummary();

    // Return good completion status
    // Don't use exit() or destructor won't get called
    return 0;
}