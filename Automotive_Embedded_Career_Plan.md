# 🚗 Automotive Embedded Software Developer — Career Plan

**Profile:** Electrical Engineering + Masters | Intermediate Coder | Target: Automotive ECU / CAN / AUTOSAR

---

## 📅 PART 1: Week-by-Week Study Schedule (18 Months)

---

### 🔵 PHASE 1 — Core Embedded Fundamentals (Weeks 1–12)

#### Month 1 (Weeks 1–4) — Advanced C & Microcontroller Basics

| Week | Topic | Daily Goal (1–2 hrs) | Deliverable |
|------|-------|----------------------|-------------|
| Week 1 | Advanced C: Pointers, memory, bit manipulation | 1 concept + 2 exercises/day | Solve 20 bit-manipulation problems |
| Week 2 | Advanced C: Structs, unions, function pointers, volatile/const | 1 concept + code daily | Write a linked list in C |
| Week 3 | STM32 Setup: GPIO, clock config, HAL library | Watch tutorial + replicate | Blink LED, read button state |
| Week 4 | STM32 Timers & Interrupts | Timer-based project daily | PWM signal generation |

**Resources:** "C Programming: A Modern Approach" (King), ControllersTech YouTube, STM32 Nucleo board

---

#### Month 2 (Weeks 5–8) — Communication Protocols

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 5 | UART: Theory, registers, baud rate | Implement from scratch | STM32 ↔ PC serial console |
| Week 6 | SPI: Master-slave, chip select, modes | 1 device per day | Communicate with SPI sensor |
| Week 7 | I2C: Addressing, ACK/NACK, clock stretching | Debug with logic analyzer | Read I2C temperature sensor |
| Week 8 | Protocol Integration Project | Build daily, test daily | Multi-sensor data logger (UART + I2C + SPI) |

---

#### Month 3 (Weeks 9–12) — CAN Bus Deep Dive

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 9 | CAN theory: frame format, arbitration, bit stuffing | Read spec + simulate | Draw CAN frame on paper, verify with tool |
| Week 10 | CAN hardware: MCP2515 + STM32 | Wire up + code daily | Send/receive CAN frames |
| Week 11 | CAN error handling: error frames, bus-off, passive | Inject errors + observe | Error recovery demo |
| Week 12 | BUSMASTER tool + CAN simulation | 1 scenario/day | Simulated 2-node CAN network |

---

### 🟡 PHASE 2 — Automotive Protocols & Tools (Weeks 13–24)

#### Month 4 (Weeks 13–16) — LIN & Diagnostics

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 13 | LIN Bus: master/slave frame, schedule table | Code + test | LIN master on STM32 |
| Week 14 | UDS Protocol: session control, ECU reset (0x10, 0x11) | 1 service/day | Implement 3 UDS services |
| Week 15 | UDS Diagnostics: read DTC (0x19), read data (0x22) | 1 service/day | Full diagnostic session demo |
| Week 16 | CANoe Trial / BUSMASTER: send/receive, logging | 2 hrs tool daily | Capture and analyze real CAN traffic |

---

#### Month 5 (Weeks 17–20) — RTOS Fundamentals

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 17 | FreeRTOS basics: tasks, scheduler, priorities | 1 concept + code | 3 concurrent tasks on STM32 |
| Week 18 | FreeRTOS: Queues & Semaphores | 1 IPC mechanism/day | Producer-consumer with queue |
| Week 19 | FreeRTOS: Mutexes, event groups, timers | 1 mechanism/day | Resource-shared LED controller |
| Week 20 | RTOS Project: CAN + FreeRTOS integration | Full project build | CAN data logger with RTOS tasks |

---

#### Month 6 (Weeks 21–24) — AUTOSAR Introduction

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 21 | AUTOSAR architecture: layered model, BSW, RTE, SWC | Read + diagram | Draw AUTOSAR stack from memory |
| Week 22 | MCAL: CAN driver, Port driver, ADC driver | Study BSW config | Configure MCAL layer manually |
| Week 23 | COM Stack: PDU Router, COM module, Signal mapping | Trace message path | Document signal flow diagram |
| Week 24 | Arctic Core (open-source AUTOSAR): install + explore | 2 hrs exploration | Run sample AUTOSAR config |

---

### 🟠 PHASE 3 — Industry Standards & Safety (Weeks 25–36)

#### Month 7 (Weeks 25–28) — MISRA C & Coding Standards

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 25 | MISRA C:2012 rules overview (Mandatory + Required) | 5 rules/day | Annotated rule summary doc |
| Week 26 | MISRA violations: identify + fix in sample code | Fix 10 violations/day | Refactored MISRA-compliant module |
| Week 27 | Static analysis tools: Cppcheck (free), PC-lint | Run on your code daily | Zero-warning codebase |
| Week 28 | Code review practice: automotive naming, comments | Review daily | Clean, documented C module |

---

#### Month 8 (Weeks 29–32) — ISO 26262 & Functional Safety

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 29 | ISO 26262 overview: hazard analysis, ASIL levels | Read 2 sections/day | Summarize ASIL A–D differences |
| Week 30 | Safety concepts: safe state, redundancy, watchdog | 1 concept + code | Implement software watchdog |
| Week 31 | Safety in software: defensive coding, error handling | Apply to your code | Add safety checks to past projects |
| Week 32 | Review & document safety strategy | Full review | Safety concept document for 1 project |

---

#### Month 9 (Weeks 33–36) — DevTools & Build Systems

| Week | Topic | Daily Goal | Deliverable |
|------|-------|------------|-------------|
| Week 33 | Git: branching, rebasing, cherry-pick | 1 git operation/day | Multi-branch project on GitHub |
| Week 34 | Make & CMake: write build files from scratch | Build 1 project/day | CMake-based embedded project |
| Week 35 | Python for embedded testing: pytest, python-can library | 1 test script/day | Automated CAN test suite |
| Week 36 | Jenkins basics: CI pipeline, automated build trigger | Set up pipeline | Auto-build + test on commit |

---

### 🟢 PHASE 4 — Portfolio & Job Prep (Weeks 37–52)

#### Months 10–12 (Weeks 37–48) — Project Polish & Interviews

| Week | Focus | Goal |
|------|-------|------|
| Week 37–39 | Polish Project 1 (CAN Data Logger) | README, docs, video demo |
| Week 40–42 | Polish Project 2 (RTOS Scheduler) | GitHub, schematic, blog post |
| Week 43–45 | Polish Project 3 (UDS Diagnostic Tool) | Python GUI + CAN backend |
| Week 46–48 | Interview prep: RTOS internals, C puzzles, protocol Q&A | 10 questions/day |

#### Months 13–18 (Weeks 49–72) — Active Job Search

- Apply to 5–10 companies/week
- Network on LinkedIn with Bosch, KPIT, Tata Elxsi, Continental engineers
- Attend embedded/automotive webinars
- Keep learning: OTA updates, Ethernet/DoIP, Adaptive AUTOSAR

---

## 🛠️ PART 2: Top 5 Portfolio Projects

---

### Project 1: CAN Data Logger
**Difficulty:** Beginner-Intermediate | **Duration:** 2–3 weeks

**Description:** Two STM32 boards communicate over CAN. One sends sensor data (temperature, voltage), the other logs it to UART and displays on PC.

**Tech Stack:** STM32, MCP2515, FreeRTOS, CAN, UART, BUSMASTER

**Skills Demonstrated:** CAN framing, multi-task RTOS, hardware debugging

**Deliverables for GitHub:**
- Source code (bare-metal + FreeRTOS version)
- Wiring schematic (KiCad or hand-drawn scan)
- README with setup instructions
- Demo video (30–60 seconds)

---

### Project 2: UDS Diagnostic Tool
**Difficulty:** Intermediate | **Duration:** 3–4 weeks

**Description:** Python-based tool that sends UDS requests over CAN to a simulated ECU (STM32). Supports session control, DTC reading, live data reading.

**Tech Stack:** Python, python-can, STM32, MCP2515, UDS (ISO 14229)

**Skills Demonstrated:** Automotive diagnostics, Python scripting, CAN protocol, UDS services

**Deliverables for GitHub:**
- Python CLI tool with argparse
- STM32 UDS responder firmware
- Documentation of implemented UDS services
- Test cases with pytest

---

### Project 3: RTOS-Based ECU Simulator
**Difficulty:** Intermediate | **Duration:** 3–4 weeks

**Description:** Simulate a basic automotive ECU using FreeRTOS — separate tasks for sensor acquisition, control logic, CAN transmission, and fault monitoring with watchdog.

**Tech Stack:** STM32, FreeRTOS, CAN, Watchdog Timer

**Skills Demonstrated:** RTOS design, task prioritization, fault handling, ISO 26262 concepts

**Deliverables for GitHub:**
- Task architecture diagram
- Annotated source code
- Fault injection test results

---

### Project 4: LIN Bus Master-Slave System
**Difficulty:** Intermediate | **Duration:** 2–3 weeks

**Description:** STM32 as LIN master controls 2 slave nodes (Arduino/STM32). Slaves control LEDs/motors based on LIN schedule table commands.

**Tech Stack:** STM32, LIN bus, UART, schedule table

**Skills Demonstrated:** LIN protocol, schedule-based communication, multi-node embedded system

**Deliverables for GitHub:**
- LIN frame implementation from scratch
- Schedule table implementation
- Video of slave nodes responding to master

---

### Project 5: MISRA-Compliant Sensor Library
**Difficulty:** Intermediate-Advanced | **Duration:** 2–3 weeks

**Description:** Write a clean, MISRA C:2012 compliant sensor abstraction library for temperature + accelerometer sensors with full unit tests.

**Tech Stack:** C, Cppcheck, Unity Test Framework, STM32

**Skills Demonstrated:** Coding standards, test-driven development, static analysis

**Deliverables for GitHub:**
- MISRA-annotated C library
- Cppcheck zero-warning report
- Full unit test suite with 90%+ coverage

---

## 📄 PART 3: Resume Template

---

# [YOUR NAME]
📍 [City, India] | 📧 email@gmail.com | 📱 +91-XXXXXXXXXX
🔗 linkedin.com/in/yourname | 💻 github.com/yourname

---

## OBJECTIVE

Results-driven Electrical Engineer with M.Tech background seeking an Automotive Embedded Software Developer role. Hands-on experience in STM32 microcontrollers, CAN/LIN protocols, FreeRTOS, and UDS diagnostics. Passionate about building reliable, safety-critical embedded systems for the automotive domain.

---

## TECHNICAL SKILLS

| Category | Skills |
|----------|--------|
| Languages | C (Advanced), Python, Embedded C |
| Microcontrollers | STM32 (Nucleo/Discovery), AVR |
| Protocols | CAN, LIN, UART, SPI, I2C, UDS (ISO 14229) |
| RTOS | FreeRTOS (tasks, queues, semaphores, mutexes) |
| Automotive | AUTOSAR Classic (BSW/RTE/SWC concepts), MISRA C:2012, ISO 26262 (basics) |
| Tools | BUSMASTER, CANoe (trial), Git, CMake, Cppcheck, Logic Analyzer |
| Testing | pytest, python-can, Unity Test Framework |

---

## PROJECTS

### CAN Data Logger | STM32, FreeRTOS, MCP2515, CAN
*[Month Year]*
- Designed dual-node CAN communication system using STM32 microcontrollers and MCP2515 CAN controller
- Implemented FreeRTOS tasks for sensor acquisition, CAN transmission, and UART logging with priority management
- Achieved reliable message transmission at 500 kbps with error detection and recovery mechanism
- Validated system using BUSMASTER tool; captured and analyzed 1000+ CAN frames
- **GitHub:** github.com/yourname/can-data-logger

---

### UDS Diagnostic Tool | Python, python-can, STM32, ISO 14229
*[Month Year]*
- Built Python CLI tool supporting 5 UDS services: Session Control (0x10), ECU Reset (0x11), Read DTC (0x19), Read Data (0x22), Clear DTC (0x14)
- Developed STM32-based UDS responder firmware simulating a real ECU diagnostic interface
- Wrote 30+ automated pytest test cases covering nominal and error scenarios
- Reduced manual diagnostic test time by 70% compared to manual CAN frame injection
- **GitHub:** github.com/yourname/uds-diagnostic-tool

---

### RTOS-Based ECU Simulator | STM32, FreeRTOS, CAN, Watchdog
*[Month Year]*
- Architected a 5-task RTOS system (sensor, control, CAN TX, fault monitor, watchdog) for ECU simulation
- Implemented software watchdog with automatic safe-state recovery aligned with ISO 26262 concepts
- Documented task architecture and timing analysis; achieved deterministic 10ms control cycle
- **GitHub:** github.com/yourname/rtos-ecu-simulator

---

## EDUCATION

**M.Tech / M.E. — [Specialization]**
[University Name], [City] | [Year]
CGPA: X.X / 10

**B.E. / B.Tech — Electrical Engineering**
[University Name], [City] | [Year]
CGPA: X.X / 10

---

## CERTIFICATIONS (Add as you earn them)
- [ ] Udemy: Embedded Systems STM32 — FastBit EBA
- [ ] FreeRTOS Developer Certification
- [ ] Vector AUTOSAR Training (online)
- [ ] ISTQB Foundation (Embedded Testing)

---

## KEY STRENGTHS FOR AUTOMOTIVE EMBEDDED
- Strong hardware background (EE degree) — understands signal integrity, power electronics, PCB
- Comfortable reading datasheets, reference manuals, and protocol specifications
- Experience with oscilloscopes and logic analyzers for hardware debugging
- Systematic approach to debugging: software + hardware boundary

---

*Last Updated: [Month Year]*

---

## 🎯 Target Companies (India)

| Company | Roles | Location |
|---------|-------|----------|
| KPIT Technologies | Embedded SW Engineer | Pune, Bangalore |
| Tata Elxsi | Automotive Embedded | Bangalore, Pune |
| Bosch | ECU Software Developer | Coimbatore, Bangalore |
| Continental | Embedded Engineer | Bangalore, Chennai |
| Aptiv | SW Developer Automotive | Hyderabad |
| Harman | Embedded Systems | Bangalore |
| Valeo | Embedded SW | Chennai, Pune |
| L&T Technology Services | Automotive SW | Mysore, Chennai |

---

*Plan created for career transition to Automotive Embedded Software Development*
*Estimated timeline: 12–18 months to first job offer*
