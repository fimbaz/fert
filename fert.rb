require 'pry'
ElementMasses = Hash[File.read("elements").split("\n").map do |x|
                       symbol, mass = x.split(' ')
                       [symbol, mass.to_i]
                     end]

class Fertilizer
  attr_accessor :elements,:formula,:compbymass,:molar_mass
  def initialize(fmla)
    _parse_fmla(fmla)
    @formula = fmla
  end

  def percentages
    @percentages ||= Hash[@elements.map do |x| [x[0],x[1] * ElementMasses[x[0]].to_f/molar_mass*100] end]
  end

  def _parse_fmla(fmla)
    @elements = Hash[fmla.scan(/([A-Z][a-z]?)(\d*)/).map do |r|
      element, count = r[0] , r[1] == ""  ? 1 : r[1].to_i
                     end]
    @molar_mass = @elements.inject(0) do |tot,x| tot + x[1] * ElementMasses[x[0]] end
          
  end

  def to_s
    s = [@formula]
    s << @elements.map do |x|
      "%s: %02d" %  [x[0],percentages[x[0]]]
    end
    s.join("\n") + "\n"
  end
end
print Fertilizer.new("KNO3")
print Fertilizer.new("KH2PO4")


# Input: desired ppm of each element




