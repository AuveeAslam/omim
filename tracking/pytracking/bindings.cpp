#include "tracking/protocol.hpp"

#include "coding/traffic.hpp"

#include "pyhelpers/pair.hpp"
#include "pyhelpers/vector_uint8.hpp"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


BOOST_PYTHON_MODULE(pytracking)
{
  using namespace boost::python;
  using tracking::Protocol;

  // Register the to-python converters.
  pair_to_python_converter<Protocol::PacketType, size_t>();
  to_python_converter<vector<uint8_t>, vector_uint8t_to_str>();
  vector_uint8t_from_python_str();

  class_<Protocol::DataElementsVec>("DataElementsVec")
      .def(vector_indexing_suite<Protocol::DataElementsVec>());

  class_<ms::LatLon>("LatLon")
      .def_readwrite("lat", &ms::LatLon::lat)
      .def_readwrite("lon", &ms::LatLon::lon);

  class_<coding::TrafficGPSEncoder::DataPoint>("DataPoint")
      .def(init<uint64_t, ms::LatLon const &>())
      .def_readwrite("timestamp", &coding::TrafficGPSEncoder::DataPoint::m_timestamp)
      .def_readwrite("coords", &coding::TrafficGPSEncoder::DataPoint::m_latLon);

  enum_<Protocol::PacketType>("PacketType")
      .value("AuthV0", Protocol::PacketType::AuthV0)
      .value("DataV0", Protocol::PacketType::DataV0)
      .value("CurrentAuth", Protocol::PacketType::CurrentAuth)
      .value("CurrentData", Protocol::PacketType::CurrentData);

  vector<uint8_t> (*CreateDataPacket1)(Protocol::DataElementsCirc const &) =
      &Protocol::CreateDataPacket;
  vector<uint8_t> (*CreateDataPacket2)(Protocol::DataElementsVec const &) =
      &Protocol::CreateDataPacket;

  class_<Protocol>("Protocol")
      .def("CreateAuthPacket", &Protocol::CreateAuthPacket)
      .staticmethod("CreateAuthPacket")
      .def("CreateDataPacket", CreateDataPacket1)
      .def("CreateDataPacket", CreateDataPacket2)
      .staticmethod("CreateDataPacket")
      .def("CreateHeader", &Protocol::CreateHeader)
      .staticmethod("CreateHeader")
      .def("DecodeHeader", &Protocol::DecodeHeader)
      .staticmethod("DecodeHeader")
      .def("DecodeDataPacket", &Protocol::DecodeDataPacket)
      .staticmethod("DecodeDataPacket");
}