#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gr-gsm Livemon
# Author: Piotr Krysik
# Description: Interactive monitor of a single C0 channel with analysis performed by Wireshark (command to run wireshark: sudo wireshark -k -f udp -Y gsmtap -i lo)
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gsm
import pmt
from gnuradio import iio
from gnuradio import network
from math import pi
import gnuradio.gsm.arfcn as arfcn




class grgsm_livemon_headless_pluto(gr.top_block):

    def __init__(self, args="", collector="localhost", collectorport='4729', fc=941.8e6, gain=30, osr=4, ppm=0, samp_rate=2000000.052982, serverport='4729', shiftoff=400e3):
        gr.top_block.__init__(self, "Gr-gsm Livemon", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.args = args
        self.collector = collector
        self.collectorport = collectorport
        self.fc = fc
        self.gain = gain
        self.osr = osr
        self.ppm = ppm
        self.samp_rate = samp_rate
        self.serverport = serverport
        self.shiftoff = shiftoff

        ##################################################
        # Blocks
        ##################################################
        self.network_socket_pdu_0_0 = network.socket_pdu('UDP_CLIENT', '127.0.0.1', collectorport, 10000, False)
        self.network_socket_pdu_0 = network.socket_pdu('UDP_SERVER', '127.0.0.1', serverport, 10000, False)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('ip:pluto.local' if 'ip:pluto.local' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(int(fc-shiftoff))
        self.iio_pluto_source_0.set_samplerate(int(samp_rate))
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, gain)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.gsm_sdcch8_demapper_0 = gsm.gsm_sdcch8_demapper(
            timeslot_nr=1,
        )
        self.gsm_receiver_0 = gsm.receiver(osr, [arfcn.downlink2arfcn(fc)], [], False)
        self.gsm_message_printer_1 = gsm.message_printer(pmt.intern(""), True,
            True, True)
        self.gsm_input_0 = gsm.gsm_input(
            ppm=ppm-int(ppm),
            osr=osr,
            fc=fc,
            samp_rate_in=samp_rate,
        )
        self.gsm_decryption_0 = gsm.decryption([], 1)
        self.gsm_control_channels_decoder_0_0 = gsm.control_channels_decoder()
        self.gsm_control_channels_decoder_0 = gsm.control_channels_decoder()
        self.gsm_clock_offset_control_0 = gsm.clock_offset_control(fc-shiftoff, samp_rate, osr)
        self.gsm_bcch_ccch_demapper_0 = gsm.gsm_bcch_ccch_demapper(
            timeslot_nr=0,
        )
        self.blocks_rotator_cc_0 = blocks.rotator_cc(-2*pi*shiftoff/samp_rate, False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.gsm_bcch_ccch_demapper_0, 'bursts'), (self.gsm_control_channels_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_clock_offset_control_0, 'ctrl'), (self.gsm_input_0, 'ctrl_in'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.network_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.gsm_control_channels_decoder_0_0, 'msgs'), (self.network_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.gsm_decryption_0, 'bursts'), (self.gsm_control_channels_decoder_0_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_bcch_ccch_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_0, 'measurements'), (self.gsm_clock_offset_control_0, 'measurements'))
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_sdcch8_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_sdcch8_demapper_0, 'bursts'), (self.gsm_decryption_0, 'bursts'))
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.gsm_message_printer_1, 'msgs'))
        self.connect((self.blocks_rotator_cc_0, 0), (self.gsm_input_0, 0))
        self.connect((self.gsm_input_0, 0), (self.gsm_receiver_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.blocks_rotator_cc_0, 0))


    def get_args(self):
        return self.args

    def set_args(self, args):
        self.args = args

    def get_collector(self):
        return self.collector

    def set_collector(self, collector):
        self.collector = collector

    def get_collectorport(self):
        return self.collectorport

    def set_collectorport(self, collectorport):
        self.collectorport = collectorport

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.gsm_clock_offset_control_0.set_fc(self.fc-self.shiftoff)
        self.gsm_input_0.set_fc(self.fc)
        self.iio_pluto_source_0.set_frequency(int(self.fc-self.shiftoff))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.iio_pluto_source_0.set_gain(0, self.gain)

    def get_osr(self):
        return self.osr

    def set_osr(self, osr):
        self.osr = osr
        self.gsm_input_0.set_osr(self.osr)

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm
        self.gsm_input_0.set_ppm(self.ppm-int(self.ppm))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_rotator_cc_0.set_phase_inc(-2*pi*self.shiftoff/self.samp_rate)
        self.gsm_input_0.set_samp_rate_in(self.samp_rate)
        self.iio_pluto_source_0.set_samplerate(int(self.samp_rate))

    def get_serverport(self):
        return self.serverport

    def set_serverport(self, serverport):
        self.serverport = serverport

    def get_shiftoff(self):
        return self.shiftoff

    def set_shiftoff(self, shiftoff):
        self.shiftoff = shiftoff
        self.blocks_rotator_cc_0.set_phase_inc(-2*pi*self.shiftoff/self.samp_rate)
        self.gsm_clock_offset_control_0.set_fc(self.fc-self.shiftoff)
        self.iio_pluto_source_0.set_frequency(int(self.fc-self.shiftoff))



def argument_parser():
    description = 'Interactive monitor of a single C0 channel with analysis performed by Wireshark (command to run wireshark: sudo wireshark -k -f udp -Y gsmtap -i lo)'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--args", dest="args", type=str, default="",
        help="Set Device Arguments [default=%(default)r]")
    parser.add_argument(
        "--collector", dest="collector", type=str, default="localhost",
        help="Set IP or DNS name of collector point [default=%(default)r]")
    parser.add_argument(
        "--collectorport", dest="collectorport", type=str, default='4729',
        help="Set UDP port number of collector [default=%(default)r]")
    parser.add_argument(
        "-f", "--fc", dest="fc", type=eng_float, default=eng_notation.num_to_str(float(941.8e6)),
        help="Set GSM channel's central frequency [default=%(default)r]")
    parser.add_argument(
        "-g", "--gain", dest="gain", type=eng_float, default=eng_notation.num_to_str(float(30)),
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "--osr", dest="osr", type=intx, default=4,
        help="Set OverSampling Ratio [default=%(default)r]")
    parser.add_argument(
        "-p", "--ppm", dest="ppm", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set ppm [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float(2000000.052982)),
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--serverport", dest="serverport", type=str, default='4729',
        help="Set UDP server listening port [default=%(default)r]")
    parser.add_argument(
        "-o", "--shiftoff", dest="shiftoff", type=eng_float, default=eng_notation.num_to_str(float(400e3)),
        help="Set Frequency Shiftoff [default=%(default)r]")
    return parser


def main(top_block_cls=grgsm_livemon_headless_pluto, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(args=options.args, collector=options.collector, collectorport=options.collectorport, fc=options.fc, gain=options.gain, osr=options.osr, ppm=options.ppm, samp_rate=options.samp_rate, serverport=options.serverport, shiftoff=options.shiftoff)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
