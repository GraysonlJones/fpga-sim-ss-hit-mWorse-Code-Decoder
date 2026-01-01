// Derived from Verilator example: https://github.com/verilator/verilator/blob/master/examples/make_tracing_c/sim_main.cpp
// Original file was released under CC0 (public domain) by original author Wilson Snyder

// For std::unique_ptr
#include <memory>
// Output stuff
#include <cstdio>
#include <iostream>
#include <string>
#include <bitset>

#include <array>

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
        std::string name;

        unsigned int value;
        int mask;
    public:
        // Returns boolean for if the state has changed, and a string represenation of the state
        // A full correct state structure will always be sent if anything changes
        // May cause some latency so maybe cut this down if things are slow!
        std::pair<bool, std::string> poll() {
        
            unsigned int new_value = *(this->read_source) & mask;
            bool anything_new = (value != new_value);
            value = *(this->read_source) & mask;

            // unfortunately bitsets are fixed-size
            std::bitset<16> temp_bitset(new_value);
            // substr to get chars from index up \u2014 e.g. 14 to 15 for width 2
            std::string bit_string = temp_bitset.to_string().substr(16 - this->width);
            std::string message = this->name + "," + bit_string + "|";
            
      //      std::cout << this->value << std::endl;

            return std::pair<bool, std::string>(anything_new, message);
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

std::pair<std::string, std::string> split_at_comma(std::string input) {
    auto comma_index = input.find(",");
    return std::pair<std::string, std::string>(input.substr(0, comma_index), input.substr(comma_index + 1));
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

// From an input string updates the relevant component
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

void parse_and_update_input(const std::string& input_string, Vtop* top) {
    auto parts = split_string(input_string, "|");

    for(auto i : parts) {
        //std::cout << i;
        update_input(i, top);
    }
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
        OutputItem ((unsigned int*) &(top->segment), "segment", 7),
        OutputItem ((unsigned int*) &(top->dp), "dp", 1),
        OutputItem ((unsigned int*) &(top->anode), "anode", 4),
        OutputItem ((unsigned int*) &(top->lights), "lights", 16)
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
            parse_and_update_input(input, top.get()); // .get() to access inner pointer
        }

        top->clk = !(top->clk); // Flip clock

        contextp->timeInc(1);  // Advance one time unit
        top->eval(); // and run one frame of the model

        std::string print_string = "";
        bool need_to_send = false;

        for(auto &i : outputs_array) {
            auto [anything_new, message] = i.poll();
            need_to_send |= anything_new;
            print_string += message;
        }

        if(need_to_send) {
            std::cout << print_string << std::endl; // flush necessary for Python subprocess pipe
        }
        else {
           std::cout << "" << std::endl;
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